// This mapping table should match the discriminants of
// `rustdoc::html::item_type::ItemType` type in Rust.
itemTypes = [
  "mod",
  "externcrate",
  "import",
  "struct",
  "enum",
  "fn",
  "type",
  "static",
  "trait",
  "impl",
  "tymethod",
  "method",
  "structfield",
  "variant",
  "macro",
  "primitive",
  "associatedtype",
  "constant",
  "associatedconstant",
  "union",
  "foreigntype",
  "keyword",
  "existential",
  "attr",
  "derive",
  "traitalias"
];

// used for special search precedence
var TY_PRIMITIVE = itemTypes.indexOf("primitive");
var TY_KEYWORD = itemTypes.indexOf("keyword");

function getQueryStringParams() {
  return undefined;
}

/**
 * A function to compute the Levenshtein distance between two strings
 * Licensed under the Creative Commons Attribution-ShareAlike 3.0 Unported
 * Full License can be found at http://creativecommons.org/licenses/by-sa/3.0/legalcode
 * This code is an unmodified version of the code written by Marco de Wit
 * and was found at http://stackoverflow.com/a/18514751/745719
 */
var levenshtein_row2 = [];
function levenshtein(s1, s2) {
  if (s1 === s2) {
    return 0;
  }
  var s1_len = s1.length,
    s2_len = s2.length;
  if (s1_len && s2_len) {
    var i1 = 0,
      i2 = 0,
      a,
      b,
      c,
      c2,
      row = levenshtein_row2;
    while (i1 < s1_len) {
      row[i1] = ++i1;
    }
    while (i2 < s2_len) {
      c2 = s2.charCodeAt(i2);
      a = i2;
      ++i2;
      b = i2;
      for (i1 = 0; i1 < s1_len; ++i1) {
        c = a + (s1.charCodeAt(i1) !== c2 ? 1 : 0);
        a = row[i1];
        b = b < a ? (b < c ? b + 1 : c) : a < c ? a + 1 : c;
        row[i1] = b;
      }
    }
    return b;
  }
  return s1_len + s2_len;
}

const window = {};
const rootPath = "";

function initSearch(rawSearchIndex) {
  var currentResults, index, searchIndex;
  var MAX_LEV_DISTANCE = 3;
  var MAX_RESULTS = 200;
  var GENERICS_DATA = 1;
  var NAME = 0;
  var INPUTS_DATA = 0;
  var OUTPUT_DATA = 1;
  var params = getQueryStringParams();

  /**
   * Executes the query and builds an index of results
   * @param  {[Object]} query      [The user query]
   * @param  {[type]} searchWords  [The list of search words to query
   *                                against]
   * @param  {[type]} filterCrates [Crate to search in if defined]
   * @return {[type]}              [A search index of results]
   */
  function execQuery(query, searchWords, filterCrates) {
    function itemTypeFromName(typename) {
      var length = itemTypes.length;
      for (var i = 0; i < length; ++i) {
        if (itemTypes[i] === typename) {
          return i;
        }
      }
      return -1;
    }

    var valLower = query.query.toLowerCase(),
      val = valLower,
      typeFilter = itemTypeFromName(query.type),
      results = {},
      results_in_args = {},
      results_returned = {},
      split = valLower.split("::");

    var length = split.length;
    for (var z = 0; z < length; ++z) {
      if (split[z] === "") {
        split.splice(z, 1);
        z -= 1;
      }
    }

    function transformResults(results, isType) {
      var out = [];
      var length = results.length;
      for (var i = 0; i < length; ++i) {
        if (results[i].id > -1) {
          var obj = searchIndex[results[i].id];
          obj.lev = results[i].lev;
          if (isType !== true || obj.type) {
            var res = buildHrefAndPath(obj);
            obj.displayPath = pathSplitter(res[0]);
            obj.fullPath = obj.displayPath + obj.name;
            // To be sure than it some items aren't considered as duplicate.
            obj.fullPath += "|" + obj.ty;
            obj.href = res[1];
            out.push(obj);
            if (out.length >= MAX_RESULTS) {
              break;
            }
          }
        }
      }
      return out;
    }

    function sortResults(results, isType) {
      var ar = [];
      for (var entry in results) {
        if (results.hasOwnProperty(entry)) {
          ar.push(results[entry]);
        }
      }
      results = ar;
      var i;
      var nresults = results.length;
      for (i = 0; i < nresults; ++i) {
        results[i].word = searchWords[results[i].id];
        results[i].item = searchIndex[results[i].id] || {};
      }
      // if there are no results then return to default and fail
      if (results.length === 0) {
        return [];
      }

      results.sort(function(aaa, bbb) {
        var a, b;

        // sort by exact match with regard to the last word (mismatch goes later)
        a = aaa.word !== val;
        b = bbb.word !== val;
        if (a !== b) {
          return a - b;
        }

        // Sort by non levenshtein results and then levenshtein results by the distance
        // (less changes required to match means higher rankings)
        a = aaa.lev;
        b = bbb.lev;
        if (a !== b) {
          return a - b;
        }

        // sort by crate (non-current crate goes later)
        a = aaa.item.crate !== window.currentCrate;
        b = bbb.item.crate !== window.currentCrate;
        if (a !== b) {
          return a - b;
        }

        // sort by item name length (longer goes later)
        a = aaa.word.length;
        b = bbb.word.length;
        if (a !== b) {
          return a - b;
        }

        // sort by item name (lexicographically larger goes later)
        a = aaa.word;
        b = bbb.word;
        if (a !== b) {
          return a > b ? +1 : -1;
        }

        // sort by index of keyword in item name (no literal occurrence goes later)
        a = aaa.index < 0;
        b = bbb.index < 0;
        if (a !== b) {
          return a - b;
        }
        // (later literal occurrence, if any, goes later)
        a = aaa.index;
        b = bbb.index;
        if (a !== b) {
          return a - b;
        }

        // special precedence for primitive and keyword pages
        if (
          (aaa.item.ty === TY_PRIMITIVE && bbb.item.ty !== TY_KEYWORD) ||
          (aaa.item.ty === TY_KEYWORD && bbb.item.ty !== TY_PRIMITIVE)
        ) {
          return -1;
        }
        if (
          (bbb.item.ty === TY_PRIMITIVE && aaa.item.ty !== TY_PRIMITIVE) ||
          (bbb.item.ty === TY_KEYWORD && aaa.item.ty !== TY_KEYWORD)
        ) {
          return 1;
        }

        // sort by description (no description goes later)
        a = aaa.item.desc === "";
        b = bbb.item.desc === "";
        if (a !== b) {
          return a - b;
        }

        // sort by type (later occurrence in `itemTypes` goes later)
        a = aaa.item.ty;
        b = bbb.item.ty;
        if (a !== b) {
          return a - b;
        }

        // sort by path (lexicographically larger goes later)
        a = aaa.item.path;
        b = bbb.item.path;
        if (a !== b) {
          return a > b ? +1 : -1;
        }

        // que sera, sera
        return 0;
      });

      var length = results.length;
      for (i = 0; i < length; ++i) {
        var result = results[i];

        // this validation does not make sense when searching by types
        if (result.dontValidate) {
          continue;
        }
        var name = result.item.name.toLowerCase(),
          path = result.item.path.toLowerCase(),
          parent = result.item.parent;

        if (
          isType !== true &&
          validateResult(name, path, split, parent) === false
        ) {
          result.id = -1;
        }
      }
      return transformResults(results);
    }

    function extractGenerics(val) {
      val = val.toLowerCase();
      if (val.indexOf("<") !== -1) {
        var values = val.substring(val.indexOf("<") + 1, val.lastIndexOf(">"));
        return {
          name: val.substring(0, val.indexOf("<")),
          generics: values.split(/\s*,\s*/)
        };
      }
      return {
        name: val,
        generics: []
      };
    }

    function checkGenerics(obj, val) {
      // The names match, but we need to be sure that all generics kinda
      // match as well.
      var lev_distance = MAX_LEV_DISTANCE + 1;
      if (val.generics.length > 0) {
        if (
          obj.length > GENERICS_DATA &&
          obj[GENERICS_DATA].length >= val.generics.length
        ) {
          var elems = obj[GENERICS_DATA].slice(0);
          var total = 0;
          var done = 0;
          // We need to find the type that matches the most to remove it in order
          // to move forward.
          var vlength = val.generics.length;
          for (var y = 0; y < vlength; ++y) {
            var lev = { pos: -1, lev: MAX_LEV_DISTANCE + 1 };
            var elength = elems.length;
            for (var x = 0; x < elength; ++x) {
              var tmp_lev = levenshtein(elems[x], val.generics[y]);
              if (tmp_lev < lev.lev) {
                lev.lev = tmp_lev;
                lev.pos = x;
              }
            }
            if (lev.pos !== -1) {
              elems.splice(lev.pos, 1);
              lev_distance = Math.min(lev.lev, lev_distance);
              total += lev.lev;
              done += 1;
            } else {
              return MAX_LEV_DISTANCE + 1;
            }
          }
          return Math.ceil(total / done);
        }
      }
      return MAX_LEV_DISTANCE + 1;
    }

    // Check for type name and type generics (if any).
    function checkType(obj, val, literalSearch) {
      var lev_distance = MAX_LEV_DISTANCE + 1;
      var x;
      if (obj[NAME] === val.name) {
        if (literalSearch === true) {
          if (val.generics && val.generics.length !== 0) {
            if (
              obj.length > GENERICS_DATA &&
              obj[GENERICS_DATA].length >= val.generics.length
            ) {
              var elems = obj[GENERICS_DATA].slice(0);
              var allFound = true;

              for (
                var y = 0;
                allFound === true && y < val.generics.length;
                ++y
              ) {
                allFound = false;
                for (x = 0; allFound === false && x < elems.length; ++x) {
                  allFound = elems[x] === val.generics[y];
                }
                if (allFound === true) {
                  elems.splice(x - 1, 1);
                }
              }
              if (allFound === true) {
                return true;
              }
            } else {
              return false;
            }
          }
          return true;
        }
        // If the type has generics but don't match, then it won't return at this point.
        // Otherwise, `checkGenerics` will return 0 and it'll return.
        if (obj.length > GENERICS_DATA && obj[GENERICS_DATA].length !== 0) {
          var tmp_lev = checkGenerics(obj, val);
          if (tmp_lev <= MAX_LEV_DISTANCE) {
            return tmp_lev;
          }
        } else {
          return 0;
        }
      }
      // Names didn't match so let's check if one of the generic types could.
      if (literalSearch === true) {
        if (obj.length > GENERICS_DATA && obj[GENERICS_DATA].length > 0) {
          var length = obj[GENERICS_DATA].length;
          for (x = 0; x < length; ++x) {
            if (obj[GENERICS_DATA][x] === val.name) {
              return true;
            }
          }
        }
        return false;
      }
      lev_distance = Math.min(levenshtein(obj[NAME], val.name), lev_distance);
      if (lev_distance <= MAX_LEV_DISTANCE) {
        // The generics didn't match but the name kinda did so we give it
        // a levenshtein distance value that isn't *this* good so it goes
        // into the search results but not too high.
        lev_distance = Math.ceil((checkGenerics(obj, val) + lev_distance) / 2);
      } else if (obj.length > GENERICS_DATA && obj[GENERICS_DATA].length > 0) {
        // We can check if the type we're looking for is inside the generics!
        var olength = obj[GENERICS_DATA].length;
        for (x = 0; x < olength; ++x) {
          lev_distance = Math.min(
            levenshtein(obj[GENERICS_DATA][x], val.name),
            lev_distance
          );
        }
      }
      // Now whatever happens, the returned distance is "less good" so we should mark it
      // as such, and so we add 1 to the distance to make it "less good".
      return lev_distance + 1;
    }

    function findArg(obj, val, literalSearch) {
      var lev_distance = MAX_LEV_DISTANCE + 1;

      if (
        obj &&
        obj.type &&
        obj.type[INPUTS_DATA] &&
        obj.type[INPUTS_DATA].length > 0
      ) {
        var length = obj.type[INPUTS_DATA].length;
        for (var i = 0; i < length; i++) {
          var tmp = checkType(obj.type[INPUTS_DATA][i], val, literalSearch);
          if (literalSearch === true && tmp === true) {
            return true;
          }
          lev_distance = Math.min(tmp, lev_distance);
          if (lev_distance === 0) {
            return 0;
          }
        }
      }
      return literalSearch === true ? false : lev_distance;
    }

    function checkReturned(obj, val, literalSearch) {
      var lev_distance = MAX_LEV_DISTANCE + 1;

      if (obj && obj.type && obj.type.length > OUTPUT_DATA) {
        var ret = obj.type[OUTPUT_DATA];
        if (!obj.type[OUTPUT_DATA].length) {
          ret = [ret];
        }
        for (var x = 0; x < ret.length; ++x) {
          var r = ret[x];
          if (typeof r === "string") {
            r = [r];
          }
          var tmp = checkType(r, val, literalSearch);
          if (literalSearch === true) {
            if (tmp === true) {
              return true;
            }
            continue;
          }
          lev_distance = Math.min(tmp, lev_distance);
          if (lev_distance === 0) {
            return 0;
          }
        }
      }
      return literalSearch === true ? false : lev_distance;
    }

    function checkPath(contains, lastElem, ty) {
      if (contains.length === 0) {
        return 0;
      }
      var ret_lev = MAX_LEV_DISTANCE + 1;
      var path = ty.path.split("::");

      if (ty.parent && ty.parent.name) {
        path.push(ty.parent.name.toLowerCase());
      }

      var length = path.length;
      var clength = contains.length;
      if (clength > length) {
        return MAX_LEV_DISTANCE + 1;
      }
      for (var i = 0; i < length; ++i) {
        if (i + clength > length) {
          break;
        }
        var lev_total = 0;
        var aborted = false;
        for (var x = 0; x < clength; ++x) {
          var lev = levenshtein(path[i + x], contains[x]);
          if (lev > MAX_LEV_DISTANCE) {
            aborted = true;
            break;
          }
          lev_total += lev;
        }
        if (aborted === false) {
          ret_lev = Math.min(ret_lev, Math.round(lev_total / clength));
        }
      }
      return ret_lev;
    }

    function typePassesFilter(filter, type) {
      // No filter
      if (filter < 0) return true;

      // Exact match
      if (filter === type) return true;

      // Match related items
      var name = itemTypes[type];
      switch (itemTypes[filter]) {
        case "constant":
          return name == "associatedconstant";
        case "fn":
          return name == "method" || name == "tymethod";
        case "type":
          return name == "primitive" || name == "keyword";
      }

      // No match
      return false;
    }

    function generateId(ty) {
      if (ty.parent && ty.parent.name) {
        return itemTypes[ty.ty] + ty.path + ty.parent.name + ty.name;
      }
      return itemTypes[ty.ty] + ty.path + ty.name;
    }

    // quoted values mean literal search
    var nSearchWords = searchWords.length;
    var i;
    var ty;
    var fullId;
    var returned;
    var in_args;
    if (
      (val.charAt(0) === '"' || val.charAt(0) === "'") &&
      val.charAt(val.length - 1) === val.charAt(0)
    ) {
      val = extractGenerics(val.substr(1, val.length - 2));
      for (i = 0; i < nSearchWords; ++i) {
        if (
          filterCrates !== undefined &&
          searchIndex[i].crate !== filterCrates
        ) {
          continue;
        }
        in_args = findArg(searchIndex[i], val, true);
        returned = checkReturned(searchIndex[i], val, true);
        ty = searchIndex[i];
        fullId = generateId(ty);

        if (searchWords[i] === val.name) {
          // filter type: ... queries
          if (
            typePassesFilter(typeFilter, searchIndex[i].ty) &&
            results[fullId] === undefined
          ) {
            results[fullId] = { id: i, index: -1 };
          }
        } else if (
          (in_args === true || returned === true) &&
          typePassesFilter(typeFilter, searchIndex[i].ty)
        ) {
          if (in_args === true || returned === true) {
            if (in_args === true) {
              results_in_args[fullId] = {
                id: i,
                index: -1,
                dontValidate: true
              };
            }
            if (returned === true) {
              results_returned[fullId] = {
                id: i,
                index: -1,
                dontValidate: true
              };
            }
          } else {
            results[fullId] = {
              id: i,
              index: -1,
              dontValidate: true
            };
          }
        }
      }
      query.inputs = [val];
      query.output = val;
      query.search = val;
      // searching by type
    } else if (val.search("->") > -1) {
      var trimmer = function(s) {
        return s.trim();
      };
      var parts = val.split("->").map(trimmer);
      var input = parts[0];
      // sort inputs so that order does not matter
      var inputs = input
        .split(",")
        .map(trimmer)
        .sort();
      for (i = 0; i < inputs.length; ++i) {
        inputs[i] = extractGenerics(inputs[i]);
      }
      var output = extractGenerics(parts[1]);

      for (i = 0; i < nSearchWords; ++i) {
        if (
          filterCrates !== undefined &&
          searchIndex[i].crate !== filterCrates
        ) {
          continue;
        }
        var type = searchIndex[i].type;
        ty = searchIndex[i];
        if (!type) {
          continue;
        }
        fullId = generateId(ty);

        // allow searching for void (no output) functions as well
        var typeOutput =
          type.length > OUTPUT_DATA ? type[OUTPUT_DATA].name : "";
        returned = checkReturned(ty, output, true);
        if (output.name === "*" || returned === true) {
          in_args = false;
          var is_module = false;

          if (input === "*") {
            is_module = true;
          } else {
            var allFound = true;
            for (var it = 0; allFound === true && it < inputs.length; it++) {
              allFound = checkType(type, inputs[it], true);
            }
            in_args = allFound;
          }
          if (in_args === true) {
            results_in_args[fullId] = {
              id: i,
              index: -1,
              dontValidate: true
            };
          }
          if (returned === true) {
            results_returned[fullId] = {
              id: i,
              index: -1,
              dontValidate: true
            };
          }
          if (is_module === true) {
            results[fullId] = {
              id: i,
              index: -1,
              dontValidate: true
            };
          }
        }
      }
      query.inputs = inputs.map(function(input) {
        return input.name;
      });
      query.output = output.name;
    } else {
      query.inputs = [val];
      query.output = val;
      query.search = val;
      // gather matching search results up to a certain maximum
      val = val.replace(/\_/g, "");

      var valGenerics = extractGenerics(val);

      var paths = valLower.split("::");
      var j;
      for (j = 0; j < paths.length; ++j) {
        if (paths[j] === "") {
          paths.splice(j, 1);
          j -= 1;
        }
      }
      val = paths[paths.length - 1];
      var contains = paths.slice(0, paths.length > 1 ? paths.length - 1 : 1);

      var lev;
      var lev_distance;
      for (j = 0; j < nSearchWords; ++j) {
        ty = searchIndex[j];
        if (!ty || (filterCrates !== undefined && ty.crate !== filterCrates)) {
          continue;
        }
        var lev_add = 0;
        if (paths.length > 1) {
          lev = checkPath(contains, paths[paths.length - 1], ty);
          if (lev > MAX_LEV_DISTANCE) {
            continue;
          } else if (lev > 0) {
            lev_add = lev / 10;
          }
        }

        returned = MAX_LEV_DISTANCE + 1;
        in_args = MAX_LEV_DISTANCE + 1;
        var index = -1;
        // we want lev results to go lower than others
        lev = MAX_LEV_DISTANCE + 1;
        fullId = generateId(ty);

        if (
          searchWords[j].indexOf(split[i]) > -1 ||
          searchWords[j].indexOf(val) > -1 ||
          searchWords[j].replace(/_/g, "").indexOf(val) > -1
        ) {
          // filter type: ... queries
          if (
            typePassesFilter(typeFilter, ty.ty) &&
            results[fullId] === undefined
          ) {
            index = searchWords[j].replace(/_/g, "").indexOf(val);
          }
        }
        if ((lev = levenshtein(searchWords[j], val)) <= MAX_LEV_DISTANCE) {
          if (typePassesFilter(typeFilter, ty.ty) === false) {
            lev = MAX_LEV_DISTANCE + 1;
          } else {
            lev += 1;
          }
        }
        if ((in_args = findArg(ty, valGenerics)) <= MAX_LEV_DISTANCE) {
          if (typePassesFilter(typeFilter, ty.ty) === false) {
            in_args = MAX_LEV_DISTANCE + 1;
          }
        }
        if ((returned = checkReturned(ty, valGenerics)) <= MAX_LEV_DISTANCE) {
          if (typePassesFilter(typeFilter, ty.ty) === false) {
            returned = MAX_LEV_DISTANCE + 1;
          }
        }

        lev += lev_add;
        if (lev > 0 && val.length > 3 && searchWords[j].indexOf(val) > -1) {
          if (val.length < 6) {
            lev -= 1;
          } else {
            lev = 0;
          }
        }
        if (in_args <= MAX_LEV_DISTANCE) {
          if (results_in_args[fullId] === undefined) {
            results_in_args[fullId] = {
              id: j,
              index: index,
              lev: in_args
            };
          }
          results_in_args[fullId].lev = Math.min(
            results_in_args[fullId].lev,
            in_args
          );
        }
        if (returned <= MAX_LEV_DISTANCE) {
          if (results_returned[fullId] === undefined) {
            results_returned[fullId] = {
              id: j,
              index: index,
              lev: returned
            };
          }
          results_returned[fullId].lev = Math.min(
            results_returned[fullId].lev,
            returned
          );
        }
        if (index !== -1 || lev <= MAX_LEV_DISTANCE) {
          if (index !== -1 && paths.length < 2) {
            lev = 0;
          }
          if (results[fullId] === undefined) {
            results[fullId] = {
              id: j,
              index: index,
              lev: lev
            };
          }
          results[fullId].lev = Math.min(results[fullId].lev, lev);
        }
      }
    }

    var ret = {
      in_args: sortResults(results_in_args, true),
      returned: sortResults(results_returned, true),
      others: sortResults(results)
    };
    // if (ALIASES && ALIASES[window.currentCrate] &&
    //     ALIASES[window.currentCrate][query.raw]) {
    //     var aliases = ALIASES[window.currentCrate][query.raw];
    //     for (i = 0; i < aliases.length; ++i) {
    //         aliases[i].is_alias = true;
    //         aliases[i].alias = query.raw;
    //         aliases[i].path = aliases[i].p;
    //         var res = buildHrefAndPath(aliases[i]);
    //         aliases[i].displayPath = pathSplitter(res[0]);
    //         aliases[i].fullPath = aliases[i].displayPath + aliases[i].name;
    //         aliases[i].href = res[1];
    //         ret.others.unshift(aliases[i]);
    //         if (ret.others.length > MAX_RESULTS) {
    //             ret.others.pop();
    //         }
    //     }
    // }
    return ret;
  }

  /**
   * Validate performs the following boolean logic. For example:
   * "File::open" will give IF A PARENT EXISTS => ("file" && "open")
   * exists in (name || path || parent) OR => ("file" && "open") exists in
   * (name || path )
   *
   * This could be written functionally, but I wanted to minimise
   * functions on stack.
   *
   * @param  {[string]} name   [The name of the result]
   * @param  {[string]} path   [The path of the result]
   * @param  {[string]} keys   [The keys to be used (["file", "open"])]
   * @param  {[object]} parent [The parent of the result]
   * @return {[boolean]}       [Whether the result is valid or not]
   */
  function validateResult(name, path, keys, parent) {
    for (var i = 0; i < keys.length; ++i) {
      // each check is for validation so we negate the conditions and invalidate
      if (
        !(
          // check for an exact name match
          (
            name.indexOf(keys[i]) > -1 ||
            // then an exact path match
            path.indexOf(keys[i]) > -1 ||
            // next if there is a parent, check for exact parent match
            (parent !== undefined &&
              parent.name !== undefined &&
              parent.name.toLowerCase().indexOf(keys[i]) > -1) ||
            // lastly check to see if the name was a levenshtein match
            levenshtein(name, keys[i]) <= MAX_LEV_DISTANCE
          )
        )
      ) {
        return false;
      }
    }
    return true;
  }

  function getQuery(raw) {
    var matches, type, query;
    query = raw;

    matches = query.match(
      /^(fn|mod|struct|enum|trait|type|const|macro)\s*:\s*/i
    );
    if (matches) {
      type = matches[1].replace(/^const$/, "constant");
      query = query.substring(matches[0].length);
    }

    return {
      raw: raw,
      query: query,
      type: type,
      id: query + type
    };
  }

  function initSearchNav() {
    var hoverTimeout;

    var click_func = function(e) {
      var el = e.target;
      // to retrieve the real "owner" of the event.
      while (el.tagName !== "TR") {
        el = el.parentNode;
      }
      var dst = e.target.getElementsByTagName("a");
      if (dst.length < 1) {
        return;
      }
      dst = dst[0];
      if (window.location.pathname === dst.pathname) {
        hideSearchResults();
        document.location.href = dst.href;
      }
    };
    var mouseover_func = function(e) {
      var el = e.target;
      // to retrieve the real "owner" of the event.
      while (el.tagName !== "TR") {
        el = el.parentNode;
      }
      clearTimeout(hoverTimeout);
      hoverTimeout = setTimeout(function() {
        onEachLazy(document.getElementsByClassName("search-results"), function(
          e
        ) {
          onEachLazy(e.getElementsByClassName("result"), function(i_e) {
            removeClass(i_e, "highlighted");
          });
        });
        addClass(el, "highlighted");
      }, 20);
    };
    onEachLazy(document.getElementsByClassName("search-results"), function(e) {
      onEachLazy(e.getElementsByClassName("result"), function(i_e) {
        i_e.onclick = click_func;
        i_e.onmouseover = mouseover_func;
      });
    });

    search_input.onkeydown = function(e) {
      // "actives" references the currently highlighted item in each search tab.
      // Each array in "actives" represents a tab.
      var actives = [[], [], []];
      // "current" is used to know which tab we're looking into.
      var current = 0;
      onEachLazy(document.getElementById("results").childNodes, function(e) {
        onEachLazy(e.getElementsByClassName("highlighted"), function(e) {
          actives[current].push(e);
        });
        current += 1;
      });

      if (e.which === 38) {
        // up
        if (
          !actives[currentTab].length ||
          !actives[currentTab][0].previousElementSibling
        ) {
          return;
        }

        addClass(actives[currentTab][0].previousElementSibling, "highlighted");
        removeClass(actives[currentTab][0], "highlighted");
      } else if (e.which === 40) {
        // down
        if (!actives[currentTab].length) {
          var results = document.getElementById("results").childNodes;
          if (results.length > 0) {
            var res = results[currentTab].getElementsByClassName("result");
            if (res.length > 0) {
              addClass(res[0], "highlighted");
            }
          }
        } else if (actives[currentTab][0].nextElementSibling) {
          addClass(actives[currentTab][0].nextElementSibling, "highlighted");
          removeClass(actives[currentTab][0], "highlighted");
        }
      } else if (e.which === 13) {
        // return
        if (actives[currentTab].length) {
          document.location.href = actives[currentTab][0].getElementsByTagName(
            "a"
          )[0].href;
        }
      } else if (e.which === 9) {
        // tab
        if (e.shiftKey) {
          printTab(currentTab > 0 ? currentTab - 1 : 2);
        } else {
          printTab(currentTab > 1 ? 0 : currentTab + 1);
        }
        e.preventDefault();
      } else if (e.which === 16) {
        // shift
        // Does nothing, it's just to avoid losing "focus" on the highlighted element.
      } else if (actives[currentTab].length > 0) {
        removeClass(actives[currentTab][0], "highlighted");
      }
    };
  }

  function buildHrefAndPath(item) {
    var displayPath;
    var href;
    var type = itemTypes[item.ty];
    var name = item.name;

    if (type === "mod") {
      displayPath = item.path + "::";
      href =
        rootPath + item.path.replace(/::/g, "/") + "/" + name + "/index.html";
    } else if (type === "primitive" || type === "keyword") {
      displayPath = "";
      href =
        rootPath +
        item.path.replace(/::/g, "/") +
        "/" +
        type +
        "." +
        name +
        ".html";
    } else if (type === "externcrate") {
      displayPath = "";
      href = rootPath + name + "/index.html";
    } else if (item.parent !== undefined) {
      var myparent = item.parent;
      var anchor = "#" + type + "." + name;
      var parentType = itemTypes[myparent.ty];
      if (parentType === "primitive") {
        displayPath = myparent.name + "::";
      } else {
        displayPath = item.path + "::" + myparent.name + "::";
      }
      href =
        rootPath +
        item.path.replace(/::/g, "/") +
        "/" +
        parentType +
        "." +
        myparent.name +
        ".html" +
        anchor;
    } else {
      displayPath = item.path + "::";
      href =
        rootPath +
        item.path.replace(/::/g, "/") +
        "/" +
        type +
        "." +
        name +
        ".html";
    }
    return [displayPath, href];
  }

  function escape(content) {
    var h1 = document.createElement("h1");
    h1.textContent = content;
    return h1.innerHTML;
  }

  function pathSplitter(path) {
    var tmp = "<span>" + path.replace(/::/g, "::</span><span>");
    if (tmp.endsWith("<span>")) {
      return tmp.slice(0, tmp.length - 6);
    }
    return tmp;
  }

  function addTab(array, query, display) {
    var extraStyle = "";
    if (display === false) {
      extraStyle = ' style="display: none;"';
    }

    var output = "";
    var duplicates = {};
    var length = 0;
    if (array.length > 0) {
      output = '<table class="search-results"' + extraStyle + ">";

      array.forEach(function(item) {
        var name, type;

        name = item.name;
        type = itemTypes[item.ty];

        if (item.is_alias !== true) {
          if (duplicates[item.fullPath]) {
            return;
          }
          duplicates[item.fullPath] = true;
        }
        length += 1;

        output +=
          '<tr class="' +
          type +
          ' result"><td>' +
          '<a href="' +
          item.href +
          '">' +
          (item.is_alias === true
            ? '<span class="alias"><b>' +
              item.alias +
              " </b></span><span " +
              'class="grey"><i>&nbsp;- see&nbsp;</i></span>'
            : "") +
          item.displayPath +
          '<span class="' +
          type +
          '">' +
          name +
          "</span></a></td><td>" +
          '<a href="' +
          item.href +
          '">' +
          '<span class="desc">' +
          escape(item.desc) +
          "&nbsp;</span></a></td></tr>";
      });
      output += "</table>";
    } else {
      output =
        '<div class="search-failed"' +
        extraStyle +
        ">No results :(<br/>" +
        'Try on <a href="https://duckduckgo.com/?q=' +
        encodeURIComponent("rust " + query.query) +
        '">DuckDuckGo</a>?<br/><br/>' +
        "Or try looking in one of these:<ul><li>The <a " +
        'href="https://doc.rust-lang.org/reference/index.html">Rust Reference</a> ' +
        " for technical details about the language.</li><li><a " +
        'href="https://doc.rust-lang.org/rust-by-example/index.html">Rust By ' +
        "Example</a> for expository code examples.</a></li><li>The <a " +
        'href="https://doc.rust-lang.org/book/index.html">Rust Book</a> for ' +
        "introductions to language features and the language itself.</li><li><a " +
        'href="https://docs.rs">Docs.rs</a> for documentation of crates released on' +
        ' <a href="https://crates.io/">crates.io</a>.</li></ul></div>';
    }
    return [output, length];
  }

  function makeTabHeader(tabNb, text, nbElems) {
    if (currentTab === tabNb) {
      return (
        '<div class="selected">' +
        text +
        ' <div class="count">(' +
        nbElems +
        ")</div></div>"
      );
    }
    return "<div>" + text + ' <div class="count">(' + nbElems + ")</div></div>";
  }

  function showResults(results) {
    if (
      results.others.length === 1 &&
      getCurrentValue("rustdoc-go-to-only-result") === "true"
    ) {
      var elem = document.createElement("a");
      elem.href = results.others[0].href;
      elem.style.display = "none";
      // For firefox, we need the element to be in the DOM so it can be clicked.
      document.body.appendChild(elem);
      elem.click();
    }
    var query = getQuery(search_input.value);

    currentResults = query.id;

    var ret_others = addTab(results.others, query);
    var ret_in_args = addTab(results.in_args, query, false);
    var ret_returned = addTab(results.returned, query, false);

    var output =
      "<h1>Results for " +
      escape(query.query) +
      (query.type ? " (type: " + escape(query.type) + ")" : "") +
      "</h1>" +
      '<div id="titles">' +
      makeTabHeader(0, "In Names", ret_others[1]) +
      makeTabHeader(1, "In Parameters", ret_in_args[1]) +
      makeTabHeader(2, "In Return Types", ret_returned[1]) +
      '</div><div id="results">' +
      ret_others[0] +
      ret_in_args[0] +
      ret_returned[0] +
      "</div>";

    var search = getSearchElement();
    search.innerHTML = output;
    showSearchResults(search);
    var tds = search.getElementsByTagName("td");
    var td_width = 0;
    if (tds.length > 0) {
      td_width = tds[0].offsetWidth;
    }
    var width = search.offsetWidth - 40 - td_width;
    onEachLazy(search.getElementsByClassName("desc"), function(e) {
      e.style.width = width + "px";
    });
    initSearchNav();
    var elems = document.getElementById("titles").childNodes;
    elems[0].onclick = function() {
      printTab(0);
    };
    elems[1].onclick = function() {
      printTab(1);
    };
    elems[2].onclick = function() {
      printTab(2);
    };
    printTab(currentTab);
  }

  function execSearch(query, searchWords, filterCrates) {
    function getSmallest(arrays, positions, notDuplicates) {
      var start = null;

      for (var it = 0; it < positions.length; ++it) {
        if (
          arrays[it].length > positions[it] &&
          (start === null || start > arrays[it][positions[it]].lev) &&
          !notDuplicates[arrays[it][positions[it]].fullPath]
        ) {
          start = arrays[it][positions[it]].lev;
        }
      }
      return start;
    }

    function mergeArrays(arrays) {
      var ret = [];
      var positions = [];
      var notDuplicates = {};

      for (var x = 0; x < arrays.length; ++x) {
        positions.push(0);
      }
      while (ret.length < MAX_RESULTS) {
        var smallest = getSmallest(arrays, positions, notDuplicates);

        if (smallest === null) {
          break;
        }
        for (x = 0; x < arrays.length && ret.length < MAX_RESULTS; ++x) {
          if (
            arrays[x].length > positions[x] &&
            arrays[x][positions[x]].lev === smallest &&
            !notDuplicates[arrays[x][positions[x]].fullPath]
          ) {
            ret.push(arrays[x][positions[x]]);
            notDuplicates[arrays[x][positions[x]].fullPath] = true;
            positions[x] += 1;
          }
        }
      }
      return ret;
    }

    var queries = query.raw.split(",");
    var results = {
      in_args: [],
      returned: [],
      others: []
    };

    for (var i = 0; i < queries.length; ++i) {
      query = queries[i].trim();
      if (query.length !== 0) {
        var tmp = execQuery(getQuery(query), searchWords, filterCrates);

        results.in_args.push(tmp.in_args);
        results.returned.push(tmp.returned);
        results.others.push(tmp.others);
      }
    }
    if (queries.length > 1) {
      return {
        in_args: mergeArrays(results.in_args),
        returned: mergeArrays(results.returned),
        others: mergeArrays(results.others)
      };
    } else {
      return {
        in_args: results.in_args[0],
        returned: results.returned[0],
        others: results.others[0]
      };
    }
  }

  function getFilterCrates() {
    var elem = document.getElementById("crate-search");

    if (
      elem &&
      elem.value !== "All crates" &&
      rawSearchIndex.hasOwnProperty(elem.value)
    ) {
      return elem.value;
    }
    return undefined;
  }

  function search(e, forced) {
    var params = getQueryStringParams();
    var query = getQuery(search_input.value.trim());

    if (e) {
      e.preventDefault();
    }

    if (query.query.length === 0) {
      return;
    }
    if (forced !== true && query.id === currentResults) {
      if (query.query.length > 0) {
        putBackSearch(search_input);
      }
      return;
    }

    // Update document title to maintain a meaningful browser history
    document.title = "Results for " + query.query + " - Rust";

    // Because searching is incremental by character, only the most
    // recent search query is added to the browser history.
    if (browserSupportsHistoryApi()) {
      if (!history.state && !params.search) {
        history.pushState(
          query,
          "",
          "?search=" + encodeURIComponent(query.raw)
        );
      } else {
        history.replaceState(
          query,
          "",
          "?search=" + encodeURIComponent(query.raw)
        );
      }
    }

    var filterCrates = getFilterCrates();
    showResults(execSearch(query, index, filterCrates));
  }

  function buildIndex(rawSearchIndex) {
    searchIndex = [];
    var searchWords = [];
    var i;

    for (var crate in rawSearchIndex) {
      if (!rawSearchIndex.hasOwnProperty(crate)) {
        continue;
      }

      searchWords.push(crate);
      searchIndex.push({
        crate: crate,
        ty: 1, // == ExternCrate
        name: crate,
        path: "",
        desc: rawSearchIndex[crate].doc,
        type: null
      });

      // an array of [(Number) item type,
      //              (String) name,
      //              (String) full path or empty string for previous path,
      //              (String) description,
      //              (Number | null) the parent path index to `paths`]
      //              (Object | null) the type of the function (if any)
      var items = rawSearchIndex[crate].i;
      // an array of [(Number) item type,
      //              (String) name]
      var paths = rawSearchIndex[crate].p;

      // convert `paths` into an object form
      var len = paths.length;
      for (i = 0; i < len; ++i) {
        paths[i] = { ty: paths[i][0], name: paths[i][1] };
      }

      // convert `items` into an object form, and construct word indices.
      //
      // before any analysis is performed lets gather the search terms to
      // search against apart from the rest of the data.  This is a quick
      // operation that is cached for the life of the page state so that
      // all other search operations have access to this cached data for
      // faster analysis operations
      len = items.length;
      var lastPath = "";
      for (i = 0; i < len; ++i) {
        var rawRow = items[i];
        var row = {
          crate: crate,
          ty: rawRow[0],
          name: rawRow[1],
          path: rawRow[2] || lastPath,
          desc: rawRow[3],
          parent: paths[rawRow[4]],
          type: rawRow[5]
        };
        searchIndex.push(row);
        if (typeof row.name === "string") {
          var word = row.name.toLowerCase();
          searchWords.push(word);
        } else {
          searchWords.push("");
        }
        lastPath = row.path;
      }
    }
    return searchWords;
  }

  function startSearch() {
    var searchTimeout;
    var callback = function() {
      clearTimeout(searchTimeout);
      if (search_input.value.length === 0) {
        if (browserSupportsHistoryApi()) {
          history.replaceState("", window.currentCrate + " - Rust", "?search=");
        }
        hideSearchResults();
      } else {
        searchTimeout = setTimeout(search, 500);
      }
    };
    search_input.onkeyup = callback;
    search_input.oninput = callback;
    document.getElementsByClassName("search-form")[0].onsubmit = function(e) {
      e.preventDefault();
      clearTimeout(searchTimeout);
      search();
    };
    search_input.onchange = function(e) {
      if (e.target !== document.activeElement) {
        // To prevent doing anything when it's from a blur event.
        return;
      }
      // Do NOT e.preventDefault() here. It will prevent pasting.
      clearTimeout(searchTimeout);
      // zero-timeout necessary here because at the time of event handler execution the
      // pasted content is not in the input field yet. Shouldn’t make any difference for
      // change, though.
      setTimeout(search, 0);
    };
    search_input.onpaste = search_input.onchange;

    var selectCrate = document.getElementById("crate-search");
    if (selectCrate) {
      selectCrate.onchange = function() {
        updateLocalStorage("rustdoc-saved-filter-crate", selectCrate.value);
        search(undefined, true);
      };
    }

    // Push and pop states are used to add search results to the browser
    // history.
    if (browserSupportsHistoryApi()) {
      // Store the previous <title> so we can revert back to it later.
      var previousTitle = document.title;

      window.addEventListener("popstate", function(e) {
        var params = getQueryStringParams();
        // Revert to the previous title manually since the History
        // API ignores the title parameter.
        document.title = previousTitle;
        // When browsing forward to search results the previous
        // search will be repeated, so the currentResults are
        // cleared to ensure the search is successful.
        currentResults = null;
        // Synchronize search bar with query string state and
        // perform the search. This will empty the bar if there's
        // nothing there, which lets you really go back to a
        // previous state with nothing in the bar.
        if (params.search && params.search.length > 0) {
          search_input.value = params.search;
          // Some browsers fire "onpopstate" for every page load
          // (Chrome), while others fire the event only when actually
          // popping a state (Firefox), which is why search() is
          // called both here and at the end of the startSearch()
          // function.
          search(e);
        } else {
          search_input.value = "";
          // When browsing back from search results the main page
          // visibility must be reset.
          hideSearchResults();
        }
      });
    }
    search();
  }

  index = buildIndex(rawSearchIndex);

  return query => {
    return execSearch(getQuery(query), index);
  };
}

var itemTypes = [
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
var TY_PRIMITIVE = itemTypes.indexOf("primitive");
var TY_KEYWORD = itemTypes.indexOf("keyword");
var ALIASES = {};
ALIASES["alloc"] = JSON.parse(
  '{"{}":[{"crate":"alloc","ty":8,"name":"Display","desc":"Format trait for an empty format, `{}`.","p":"alloc::fmt"}],"{:?}":[{"crate":"alloc","ty":8,"name":"Debug","desc":"`?` formatting.","p":"alloc::fmt"}]}'
);

ALIASES["core"] = JSON.stringify(
  '{"{:?}":[{"crate":"core","ty":8,"name":"Debug","desc":"`?` formatting.","p":"core::fmt"}],"..=":[{"crate":"core","ty":3,"name":"RangeInclusive","desc":"A range bounded inclusively below and above (`start..=end`).","p":"core::ops"},{"crate":"core","ty":3,"name":"RangeToInclusive","desc":"A range only bounded inclusively above (`..=end`).","p":"core::ops"}],"*":[{"crate":"core","ty":8,"name":"Mul","desc":"The multiplication operator `*`.","p":"core::ops"},{"crate":"core","ty":8,"name":"MulAssign","desc":"The multiplication assignment operator `*=`.","p":"core::ops"},{"crate":"core","ty":8,"name":"Deref","desc":"Used for immutable dereferencing operations, like `*v`.","p":"core::ops"},{"crate":"core","ty":8,"name":"DerefMut","desc":"Used for mutable dereferencing operations, like in `*v =…","p":"core::ops"}],">=":[{"crate":"core","ty":8,"name":"Ord","desc":"Trait for types that form a total order.","p":"core::cmp"},{"crate":"core","ty":8,"name":"PartialOrd","desc":"Trait for values that can be compared for a sort-order.","p":"core::cmp"}],"^=":[{"crate":"core","ty":8,"name":"BitXorAssign","desc":"The bitwise XOR assignment operator `^=`.","p":"core::ops"}],">":[{"crate":"core","ty":8,"name":"Ord","desc":"Trait for types that form a total order.","p":"core::cmp"},{"crate":"core","ty":8,"name":"PartialOrd","desc":"Trait for values that can be compared for a sort-order.","p":"core::cmp"}],"&=":[{"crate":"core","ty":8,"name":"BitAndAssign","desc":"The bitwise AND assignment operator `&=`.","p":"core::ops"}],"^":[{"crate":"core","ty":8,"name":"BitXor","desc":"The bitwise XOR operator `^`.","p":"core::ops"}],"<=":[{"crate":"core","ty":8,"name":"Ord","desc":"Trait for types that form a total order.","p":"core::cmp"},{"crate":"core","ty":8,"name":"PartialOrd","desc":"Trait for values that can be compared for a sort-order.","p":"core::cmp"}],"[]":[{"crate":"core","ty":8,"name":"Index","desc":"Used for indexing operations (`container[index]`) in…","p":"core::ops"},{"crate":"core","ty":8,"name":"IndexMut","desc":"Used for indexing operations (`container[index]`) in…","p":"core::ops"}],"+":[{"crate":"core","ty":8,"name":"Add","desc":"The addition operator `+`.","p":"core::ops"},{"crate":"core","ty":8,"name":"AddAssign","desc":"The addition assignment operator `+=`.","p":"core::ops"}],"%":[{"crate":"core","ty":8,"name":"Rem","desc":"The remainder operator `%`.","p":"core::ops"},{"crate":"core","ty":8,"name":"RemAssign","desc":"The remainder assignment operator `%=`.","p":"core::ops"}],">>=":[{"crate":"core","ty":8,"name":"ShrAssign","desc":"The right shift assignment operator `>>=`.","p":"core::ops"}],"[":[{"crate":"core","ty":8,"name":"Index","desc":"Used for indexing operations (`container[index]`) in…","p":"core::ops"},{"crate":"core","ty":8,"name":"IndexMut","desc":"Used for indexing operations (`container[index]`) in…","p":"core::ops"}],"/":[{"crate":"core","ty":8,"name":"Div","desc":"The division operator `/`.","p":"core::ops"},{"crate":"core","ty":8,"name":"DivAssign","desc":"The division assignment operator `/=`.","p":"core::ops"}],"..":[{"crate":"core","ty":3,"name":"Range","desc":"A (half-open) range bounded inclusively below and…","p":"core::ops"},{"crate":"core","ty":3,"name":"RangeFrom","desc":"A range only bounded inclusively below (`start..`).","p":"core::ops"},{"crate":"core","ty":3,"name":"RangeFull","desc":"An unbounded range (`..`).","p":"core::ops"},{"crate":"core","ty":3,"name":"RangeTo","desc":"A range only bounded exclusively above (`..end`).","p":"core::ops"}],"<<":[{"crate":"core","ty":8,"name":"Shl","desc":"The left shift operator `<<`. Note that because this trait…","p":"core::ops"}],"{}":[{"crate":"core","ty":8,"name":"Display","desc":"Format trait for an empty format, `{}`.","p":"core::fmt"}],"*=":[{"crate":"core","ty":8,"name":"MulAssign","desc":"The multiplication assignment operator `*=`.","p":"core::ops"}],"&":[{"crate":"core","ty":8,"name":"BitAnd","desc":"The bitwise AND operator `&`.","p":"core::ops"}],"|=":[{"crate":"core","ty":8,"name":"BitOrAssign","desc":"The bitwise OR assignment operator `|=`.","p":"core::ops"}],"<":[{"crate":"core","ty":8,"name":"Ord","desc":"Trait for types that form a total order.","p":"core::cmp"},{"crate":"core","ty":8,"name":"PartialOrd","desc":"Trait for values that can be compared for a sort-order.","p":"core::cmp"}],"|":[{"crate":"core","ty":8,"name":"BitOr","desc":"The bitwise OR operator `|`.","p":"core::ops"}],"&*":[{"crate":"core","ty":8,"name":"Deref","desc":"Used for immutable dereferencing operations, like `*v`.","p":"core::ops"}],">>":[{"crate":"core","ty":8,"name":"Shr","desc":"The right shift operator `>>`. Note that because this…","p":"core::ops"}],"?":[{"crate":"core","ty":8,"name":"Try","desc":"A trait for customizing the behavior of the `?` operator.","p":"core::ops"},{"crate":"core","ty":14,"name":"try","desc":"Unwraps a result or propagates its error.","p":"core"}],"-=":[{"crate":"core","ty":8,"name":"SubAssign","desc":"The subtraction assignment operator `-=`.","p":"core::ops"}],"!=":[{"crate":"core","ty":8,"name":"PartialEq","desc":"Trait for equality comparisons which are partial…","p":"core::cmp"},{"crate":"core","ty":8,"name":"Eq","desc":"Trait for equality comparisons which are equivalence…","p":"core::cmp"}],"-":[{"crate":"core","ty":8,"name":"Sub","desc":"The subtraction operator `-`.","p":"core::ops"},{"crate":"core","ty":8,"name":"Neg","desc":"The unary negation operator `-`.","p":"core::ops"},{"crate":"core","ty":8,"name":"SubAssign","desc":"The subtraction assignment operator `-=`.","p":"core::ops"}],"+=":[{"crate":"core","ty":8,"name":"AddAssign","desc":"The addition assignment operator `+=`.","p":"core::ops"}],"%=":[{"crate":"core","ty":8,"name":"RemAssign","desc":"The remainder assignment operator `%=`.","p":"core::ops"}],"<<=":[{"crate":"core","ty":8,"name":"ShlAssign","desc":"The left shift assignment operator `<<=`.","p":"core::ops"}],"/=":[{"crate":"core","ty":8,"name":"DivAssign","desc":"The division assignment operator `/=`.","p":"core::ops"}],"]":[{"crate":"core","ty":8,"name":"Index","desc":"Used for indexing operations (`container[index]`) in…","p":"core::ops"},{"crate":"core","ty":8,"name":"IndexMut","desc":"Used for indexing operations (`container[index]`) in…","p":"core::ops"}],"==":[{"crate":"core","ty":8,"name":"PartialEq","desc":"Trait for equality comparisons which are partial…","p":"core::cmp"},{"crate":"core","ty":8,"name":"Eq","desc":"Trait for equality comparisons which are equivalence…","p":"core::cmp"}]}'
);
ALIASES["proc_macro"] = {};
ALIASES["std"] = JSON.parse(
  '{"{:?}":[{"crate":"std","ty":8,"name":"Debug","desc":"`?` formatting.","p":"std::fmt"}],"!":[{"crate":"std","ty":15,"name":"never","desc":"The `!` type, also called \\"never\\".","p":"std"}],")":[{"crate":"std","ty":15,"name":"tuple","desc":"A finite heterogeneous sequence, `(T, U, ..)`.","p":"std"}],"true":[{"crate":"std","ty":15,"name":"bool","desc":"The boolean type.","p":"std"}],"*":[{"crate":"std","ty":8,"name":"Mul","desc":"The multiplication operator `*`.","p":"std::ops"},{"crate":"std","ty":8,"name":"MulAssign","desc":"The multiplication assignment operator `*=`.","p":"std::ops"},{"crate":"std","ty":8,"name":"Deref","desc":"Used for immutable dereferencing operations, like `*v`.","p":"std::ops"},{"crate":"std","ty":8,"name":"DerefMut","desc":"Used for mutable dereferencing operations, like in `*v =…","p":"std::ops"}],">=":[{"crate":"std","ty":8,"name":"Ord","desc":"Trait for types that form a total order.","p":"std::cmp"},{"crate":"std","ty":8,"name":"PartialOrd","desc":"Trait for values that can be compared for a sort-order.","p":"std::cmp"}],"..=":[{"crate":"std","ty":3,"name":"RangeInclusive","desc":"A range bounded inclusively below and above (`start..=end`).","p":"std::ops"},{"crate":"std","ty":3,"name":"RangeToInclusive","desc":"A range only bounded inclusively above (`..=end`).","p":"std::ops"}],"^=":[{"crate":"std","ty":8,"name":"BitXorAssign","desc":"The bitwise XOR assignment operator `^=`.","p":"std::ops"}],">":[{"crate":"std","ty":8,"name":"Ord","desc":"Trait for types that form a total order.","p":"std::cmp"},{"crate":"std","ty":8,"name":"PartialOrd","desc":"Trait for values that can be compared for a sort-order.","p":"std::cmp"}],"<=":[{"crate":"std","ty":8,"name":"Ord","desc":"Trait for types that form a total order.","p":"std::cmp"},{"crate":"std","ty":8,"name":"PartialOrd","desc":"Trait for values that can be compared for a sort-order.","p":"std::cmp"}],"^":[{"crate":"std","ty":8,"name":"BitXor","desc":"The bitwise XOR operator `^`.","p":"std::ops"}],"&=":[{"crate":"std","ty":8,"name":"BitAndAssign","desc":"The bitwise AND assignment operator `&=`.","p":"std::ops"}],"(":[{"crate":"std","ty":15,"name":"tuple","desc":"A finite heterogeneous sequence, `(T, U, ..)`.","p":"std"}],"[]":[{"crate":"std","ty":8,"name":"Index","desc":"Used for indexing operations (`container[index]`) in…","p":"std::ops"},{"crate":"std","ty":8,"name":"IndexMut","desc":"Used for indexing operations (`container[index]`) in…","p":"std::ops"},{"crate":"std","ty":15,"name":"slice","desc":"A dynamically-sized view into a contiguous sequence,…","p":"std"}],"+":[{"crate":"std","ty":8,"name":"Add","desc":"The addition operator `+`.","p":"std::ops"},{"crate":"std","ty":8,"name":"AddAssign","desc":"The addition assignment operator `+=`.","p":"std::ops"}],"%":[{"crate":"std","ty":8,"name":"Rem","desc":"The remainder operator `%`.","p":"std::ops"},{"crate":"std","ty":8,"name":"RemAssign","desc":"The remainder assignment operator `%=`.","p":"std::ops"}],">>=":[{"crate":"std","ty":8,"name":"ShrAssign","desc":"The right shift assignment operator `>>=`.","p":"std::ops"}],"/":[{"crate":"std","ty":8,"name":"Div","desc":"The division operator `/`.","p":"std::ops"},{"crate":"std","ty":8,"name":"DivAssign","desc":"The division assignment operator `/=`.","p":"std::ops"}],"[":[{"crate":"std","ty":8,"name":"Index","desc":"Used for indexing operations (`container[index]`) in…","p":"std::ops"},{"crate":"std","ty":8,"name":"IndexMut","desc":"Used for indexing operations (`container[index]`) in…","p":"std::ops"},{"crate":"std","ty":15,"name":"slice","desc":"A dynamically-sized view into a contiguous sequence,…","p":"std"}],"..":[{"crate":"std","ty":3,"name":"Range","desc":"A (half-open) range bounded inclusively below and…","p":"std::ops"},{"crate":"std","ty":3,"name":"RangeFrom","desc":"A range only bounded inclusively below (`start..`).","p":"std::ops"},{"crate":"std","ty":3,"name":"RangeFull","desc":"An unbounded range (`..`).","p":"std::ops"},{"crate":"std","ty":3,"name":"RangeTo","desc":"A range only bounded exclusively above (`..end`).","p":"std::ops"}],"<<":[{"crate":"std","ty":8,"name":"Shl","desc":"The left shift operator `<<`. Note that because this trait…","p":"std::ops"}],"()":[{"crate":"std","ty":15,"name":"tuple","desc":"A finite heterogeneous sequence, `(T, U, ..)`.","p":"std"}],"{}":[{"crate":"std","ty":8,"name":"Display","desc":"Format trait for an empty format, `{}`.","p":"std::fmt"}],"<":[{"crate":"std","ty":8,"name":"Ord","desc":"Trait for types that form a total order.","p":"std::cmp"},{"crate":"std","ty":8,"name":"PartialOrd","desc":"Trait for values that can be compared for a sort-order.","p":"std::cmp"}],"*=":[{"crate":"std","ty":8,"name":"MulAssign","desc":"The multiplication assignment operator `*=`.","p":"std::ops"}],"&":[{"crate":"std","ty":8,"name":"BitAnd","desc":"The bitwise AND operator `&`.","p":"std::ops"},{"crate":"std","ty":15,"name":"reference","desc":"References, both shared and mutable.","p":"std"}],"|=":[{"crate":"std","ty":8,"name":"BitOrAssign","desc":"The bitwise OR assignment operator `|=`.","p":"std::ops"}],"|":[{"crate":"std","ty":8,"name":"BitOr","desc":"The bitwise OR operator `|`.","p":"std::ops"}],"&*":[{"crate":"std","ty":8,"name":"Deref","desc":"Used for immutable dereferencing operations, like `*v`.","p":"std::ops"}],"false":[{"crate":"std","ty":15,"name":"bool","desc":"The boolean type.","p":"std"}],">>":[{"crate":"std","ty":8,"name":"Shr","desc":"The right shift operator `>>`. Note that because this…","p":"std::ops"}],"-=":[{"crate":"std","ty":8,"name":"SubAssign","desc":"The subtraction assignment operator `-=`.","p":"std::ops"}],"==":[{"crate":"std","ty":8,"name":"PartialEq","desc":"Trait for equality comparisons which are partial…","p":"std::cmp"},{"crate":"std","ty":8,"name":"Eq","desc":"Trait for equality comparisons which are equivalence…","p":"std::cmp"}],"!=":[{"crate":"std","ty":8,"name":"PartialEq","desc":"Trait for equality comparisons which are partial…","p":"std::cmp"},{"crate":"std","ty":8,"name":"Eq","desc":"Trait for equality comparisons which are equivalence…","p":"std::cmp"}],"-":[{"crate":"std","ty":8,"name":"Sub","desc":"The subtraction operator `-`.","p":"std::ops"},{"crate":"std","ty":8,"name":"Neg","desc":"The unary negation operator `-`.","p":"std::ops"},{"crate":"std","ty":8,"name":"SubAssign","desc":"The subtraction assignment operator `-=`.","p":"std::ops"}],"+=":[{"crate":"std","ty":8,"name":"AddAssign","desc":"The addition assignment operator `+=`.","p":"std::ops"}],"%=":[{"crate":"std","ty":8,"name":"RemAssign","desc":"The remainder assignment operator `%=`.","p":"std::ops"}],"]":[{"crate":"std","ty":8,"name":"Index","desc":"Used for indexing operations (`container[index]`) in…","p":"std::ops"},{"crate":"std","ty":8,"name":"IndexMut","desc":"Used for indexing operations (`container[index]`) in…","p":"std::ops"},{"crate":"std","ty":15,"name":"slice","desc":"A dynamically-sized view into a contiguous sequence,…","p":"std"}],"/=":[{"crate":"std","ty":8,"name":"DivAssign","desc":"The division assignment operator `/=`.","p":"std::ops"}],"<<=":[{"crate":"std","ty":8,"name":"ShlAssign","desc":"The left shift assignment operator `<<=`.","p":"std::ops"}],"?":[{"crate":"std","ty":8,"name":"Try","desc":"A trait for customizing the behavior of the `?` operator.","p":"std::ops"},{"crate":"std","ty":14,"name":"try","desc":"Unwraps a result or propagates its error.","p":"std"}]}'
);
ALIASES["test"] = {};
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
function initSearch(rawSearchIndex) {
  var index, searchIndex;
  var MAX_LEV_DISTANCE = 3;
  var MAX_RESULTS = 200;
  var GENERICS_DATA = 1;
  var NAME = 0;
  var INPUTS_DATA = 0;
  var OUTPUT_DATA = 1;

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
      if (results.length === 0) {
        return [];
      }
      results.sort(function(aaa, bbb) {
        var a, b;
        a = aaa.word !== val;
        b = bbb.word !== val;
        if (a !== b) {
          return a - b;
        }
        a = aaa.lev;
        b = bbb.lev;
        if (a !== b) {
          return a - b;
        }
        a = aaa.item.crate !== window.currentCrate;
        b = bbb.item.crate !== window.currentCrate;
        if (a !== b) {
          return a - b;
        }
        a = aaa.word.length;
        b = bbb.word.length;
        if (a !== b) {
          return a - b;
        }
        a = aaa.word;
        b = bbb.word;
        if (a !== b) {
          return a > b ? +1 : -1;
        }
        a = aaa.index < 0;
        b = bbb.index < 0;
        if (a !== b) {
          return a - b;
        }
        a = aaa.index;
        b = bbb.index;
        if (a !== b) {
          return a - b;
        }
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
        a = aaa.item.desc === "";
        b = bbb.item.desc === "";
        if (a !== b) {
          return a - b;
        }
        a = aaa.item.ty;
        b = bbb.item.ty;
        if (a !== b) {
          return a - b;
        }
        a = aaa.item.path;
        b = bbb.item.path;
        if (a !== b) {
          return a > b ? +1 : -1;
        }
        return 0;
      });
      var length = results.length;
      for (i = 0; i < length; ++i) {
        var result = results[i];
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
      var lev_distance = MAX_LEV_DISTANCE + 1;
      if (val.generics.length > 0) {
        if (
          obj.length > GENERICS_DATA &&
          obj[GENERICS_DATA].length >= val.generics.length
        ) {
          var elems = obj[GENERICS_DATA].slice(0);
          var total = 0;
          var done = 0;
          var vlength = val.generics.length;
          for (var y = 0; y < vlength; ++y) {
            var lev = {
              pos: -1,
              lev: MAX_LEV_DISTANCE + 1
            };
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
        if (obj.length > GENERICS_DATA && obj[GENERICS_DATA].length !== 0) {
          var tmp_lev = checkGenerics(obj, val);
          if (tmp_lev <= MAX_LEV_DISTANCE) {
            return tmp_lev;
          }
        } else {
          return 0;
        }
      }
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
        lev_distance = Math.ceil((checkGenerics(obj, val) + lev_distance) / 2);
      } else if (obj.length > GENERICS_DATA && obj[GENERICS_DATA].length > 0) {
        var olength = obj[GENERICS_DATA].length;
        for (x = 0; x < olength; ++x) {
          lev_distance = Math.min(
            levenshtein(obj[GENERICS_DATA][x], val.name),
            lev_distance
          );
        }
      }
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
    function checkPath(contains, _lastElem, ty) {
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
      if (filter < 0) return true;
      if (filter === type) return true;
      var name = itemTypes[type];
      switch (itemTypes[filter]) {
        case "constant":
          return name == "associatedconstant";
        case "fn":
          return name == "method" || name == "tymethod";
        case "type":
          return name == "primitive" || name == "keyword";
      }
      return false;
    }
    function generateId(ty) {
      if (ty.parent && ty.parent.name) {
        return itemTypes[ty.ty] + ty.path + ty.parent.name + ty.name;
      }
      return itemTypes[ty.ty] + ty.path + ty.name;
    }
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
          if (
            typePassesFilter(typeFilter, searchIndex[i].ty) &&
            results[fullId] === undefined
          ) {
            results[fullId] = {
              id: i,
              index: -1
            };
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
    } else if (val.search("->") > -1) {
      var trimmer = function(s) {
        return s.trim();
      };
      var parts = val.split("->").map(trimmer);
      var input = parts[0];
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
      for (j = 0; j < nSearchWords; ++j) {
        var lev;
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
        lev = MAX_LEV_DISTANCE + 1;
        fullId = generateId(ty);
        if (
          searchWords[j].indexOf(split[i]) > -1 ||
          searchWords[j].indexOf(val) > -1 ||
          searchWords[j].replace(/_/g, "").indexOf(val) > -1
        ) {
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
    if (
      ALIASES &&
      ALIASES[window.currentCrate] &&
      ALIASES[window.currentCrate][query.raw]
    ) {
      var aliases = ALIASES[window.currentCrate][query.raw];
      for (i = 0; i < aliases.length; ++i) {
        aliases[i].is_alias = true;
        aliases[i].alias = query.raw;
        aliases[i].path = aliases[i].p;
        var res = buildHrefAndPath(aliases[i]);
        aliases[i].displayPath = pathSplitter(res[0]);
        aliases[i].fullPath = aliases[i].displayPath + aliases[i].name;
        aliases[i].href = res[1];
        ret.others.unshift(aliases[i]);
        if (ret.others.length > MAX_RESULTS) {
          ret.others.pop();
        }
      }
    }
    return ret;
  }
  function validateResult(name, path, keys, parent) {
    for (var i = 0; i < keys.length; ++i) {
      if (
        !(
          name.indexOf(keys[i]) > -1 ||
          path.indexOf(keys[i]) > -1 ||
          (parent !== undefined &&
            parent.name.toLowerCase().indexOf(keys[i]) > -1) ||
          levenshtein(name, keys[i]) <= MAX_LEV_DISTANCE
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
  function buildHrefAndPath(item) {
    var rootPath = "";
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
  function pathSplitter(path) {
    var tmp = "<span>" + path.replace(/::/g, "::</span><span>");
    if (tmp.endsWith("<span>")) {
      return tmp.slice(0, tmp.length - 6);
    }
    return tmp;
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
        ty: 1,
        name: crate,
        path: "",
        desc: rawSearchIndex[crate].doc,
        type: null
      });
      var items = rawSearchIndex[crate].i;
      var paths = rawSearchIndex[crate].p;
      var len = paths.length;
      for (i = 0; i < len; ++i) {
        paths[i] = {
          ty: paths[i][0],
          name: paths[i][1]
        };
      }
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
  index = buildIndex(rawSearchIndex);

  return query => {
    return execSearch(getQuery(query), index);
  };
}

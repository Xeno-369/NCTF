export memory mem(initial: 1, max: 0);

data d_a(offset: 256) = "<\a7[\f0(\ded\91";
data d_oAtVOvU(offset: 272) =
":oA\9d\b3\93\0ft\8bV\04\adO\f8\aa.v~U\89\d1\e4\aa\19";

export function check(a:int, b:int):int {
  if (b != 24) { return 0 }
  var c:int = 0;
  loop L_c {
    if (c >= 24) goto B_b;
    var d:int = (a + c)[0]:ubyte;
    d = d + c & 255;
    var e:int = (256 + (c & 7))[0]:ubyte;
    d = (d | e) - (d & e);
    d = d + d + d + d + d & 255;
    if ((272 + c)[0]:ubyte != d) { return 0 }
    c = c + 1;
    continue L_c;
  }
  label B_b:
  return 1;
}


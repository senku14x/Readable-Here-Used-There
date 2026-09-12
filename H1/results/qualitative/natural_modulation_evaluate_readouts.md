# Natural modulation — qualitative readouts (J_NP top-10, interior carrier positions)

Teacher-forced text: the assistant turn is the carrier copied verbatim; nothing is generated. Position shown = middle interior token. Ranks are over the full 248k vocabulary. Selection: the fixed cells listed in `meta.json.topk_cells` plus a seeded random sample (`qual_random_cells`, seed 20260907).


## controlled|maintain|cat|C2  (user text: `Here is the word "cat". Keep that word in mind while you copy the following text exactly, …`)

| layer | top-10 at the middle interior token | rank of X over window L24-59 (min / median) |
|---|---|---|
| 23 | \n\n · \n\n\n\n · \n\n\n · <|endoftext|> ·   \n\n · a ·  • ·    ·  `` ·  \n\n | 3968 / 52280 |
| 31 |   \n\n ·    · <|endoftext|> · \n\n ·  \n\n ·    \n\n ·     · \n\n\n\n ·   \n ·   \n\n\n | 766 / 5829 |
| 35 | <|endoftext|> · \n\n ·    ·   \n\n · \n\n\n\n · \n\n\n ·  • · a ·  \n\n · <|im_end|> | 962 / 19914 |
| 39 | <|endoftext|> · \n\n · <|im_end|> ·   \n\n ·    ·  [ ·  […] ·  ... ·  \n\n · \n\n\n\n | 1953 / 30850 |
| 43 | <|im_end|> ·    · <|endoftext|> · [ ·   \n\n ·     ·  _____ ·        ·      ·  YOU | 668 / 14252 |
| 47 |   \n\n ·   \n ·  Bob ·  Queen ·  another ·  \n\n ·  White · <|im_end|> ·   ·    | 1187 / 13913 |
| 48 |   \n\n ·   \n · \\n · **! · \\u · &nbsp · <|im_end|> ·   \n  \n ·  WORD ·  TWO | 1543 / 70214 |
| 50 | ((* · **! ·  WORD · უს · *\\ · 张三 · [word · !** ·  perro · *” | 9702 / 191248 |
| 51 |  TWO ·  two ·  zwei · 两只 · two · _two · 两个 ·  deux ·  Two · .two | 5295 / 161227 |
| 55 |  two · two ·  TWO · _two ·  zwei ·  Two ·  deux · 两个 · .two · Two | 62 / 122255 |
| 59 |  two · two ·  birds ·  cats ·  Two · _two · 两只 · Two ·  TWO ·  deux | 13 / 22622 |
| 62 |  two ·  cats · two ·  cat ·  Two ·  birds ·  TWO · _two ·  deux · -two | 3 / 190 |

## controlled|mention|cat|C2  (user text: `Here is the word "cat". That word occurs one time. Now copy the following text exactly, wo…`)

| layer | top-10 at the middle interior token | rank of X over window L24-59 (min / median) |
|---|---|---|
| 23 | \n\n · <|endoftext|> · \n\n\n · \n\n\n\n ·   \n\n ·    · a ·  • · s ·  `` | 3672 / 46608 |
| 31 |   \n\n ·    · <|endoftext|> · \n\n ·  \n\n ·    \n\n · \n\n\n\n ·   \n\n\n ·     ·   \n | 844 / 7480 |
| 35 | <|endoftext|> · \n\n ·    ·   \n\n · \n\n\n\n · \n\n\n ·  ... · <|im_end|> ·  \n\n ·  • | 1492 / 15399 |
| 39 | <|endoftext|> · \n\n · <|im_end|> ·   \n\n ·    ·  […] ·  ... ·  [...] ·  \n\n · \n\n\n\n | 1043 / 19263 |
| 43 | <|im_end|> · <|endoftext|> ·    ·     ·  _____ ·   \n\n ·        ·      ·       ·  Number | 558 / 19849 |
| 47 |  two ·  TWO ·  five ·  four ·  three ·  Two ·  seven ·   \n ·  eight ·   \n\n | 390 / 27120 |
| 48 |  TWO ·  two · 两只 ·  five ·  four · two ·  twice ·  seven ·  twins ·  three | 1428 / 124007 |
| 50 | ((* · 两只 ·  TWO · **! ·  اثنين ·  zwei · *” · _two · 是两个 ·  két | 18977 / 208079 |
| 51 |  TWO ·  zwei ·  two · _two · two · 两只 ·  deux · .two · สอง ·  twins | 13949 / 188217 |
| 55 |  two ·  TWO · two · _two ·  zwei · .two ·  Two ·  deux · 两个 · Two | 1385 / 156340 |
| 59 |  two ·  birds · two · _two ·  Two · birds ·  TWO ·  Birds · Two ·  deux | 254 / 44030 |
| 62 |  two · two ·  birds ·  Two · _two ·  TWO ·  deux · -two · Two ·  tw | 87 / 1214 |

## controlled|plain_mention|cat|C2  (user text: `cat. Now copy the following text exactly, word for word:

Dust settled slowly over the vil…`)

| layer | top-10 at the middle interior token | rank of X over window L24-59 (min / median) |
|---|---|---|
| 23 | \n\n · \n\n\n · \n\n\n\n ·  • ·   \n\n · <|endoftext|> · a ·    ·  `` · • | 2358 / 56369 |
| 31 |   \n\n ·    · <|endoftext|> ·  \n\n · \n\n ·    \n\n ·   \n ·   \n\n\n · <|im_end|> · \n\n\n\n | 487 / 4350 |
| 35 | <|endoftext|> · \n\n ·   \n\n · \n\n\n\n · \n\n\n ·  \n\n ·    · <|im_end|> ·  […] ·    \n\n | 265 / 12730 |
| 39 | <|endoftext|> · \n\n · <|im_end|> ·   \n\n ·  […] ·  \n\n ·  [...] ·  ... · \n\n\n\n ·    \n\n | 301 / 5957 |
| 43 | <|im_end|> ·   \n\n · <|endoftext|> · \n\n · [ ·  […] ·    ·     · \n\n\n\n ·    \n\n | 133 / 5251 |
| 47 |   \n\n ·   \n ·  \n\n · � · &nbsp · <|im_end|> ·    \n\n ·  women · **! ·  \n | 117 / 12259 |
| 48 |   \n\n · **! · &nbsp · <|im_end|> ·   \n ·  angels · !** · 两只 · � · **” | 575 / 58506 |
| 50 | ((* · *” · **! · %X · 两只 · !* · ▪ · **” · !** · 星人 | 8249 / 228017 |
| 51 | 两位 ·  TWO ·  zwei · 两只 · _two · two ·  two · 两个 · 两名 ·  두 | 4749 / 194148 |
| 55 |  two · two ·  TWO · _two ·  zwei · 两个 ·  Two ·  deux · .two · Two | 2351 / 162361 |
| 59 |  two · two ·  birds · _two ·  Two · Two ·  TWO · 两只 ·  deux · -two | 475 / 26944 |
| 62 |  two · two ·  birds ·  Two ·  TWO · -two · _two ·  deux · Two · 两只 | 74 / 897 |

## controlled|absent|NONE|C2  (user text: `A single passage of text is given below. Now copy the following text exactly, word for wor…`)

| layer | top-10 at the middle interior token | rank of X over window L24-59 (min / median) |
|---|---|---|
| 23 | \n\n · \n\n\n · <|endoftext|> · \n\n\n\n ·  • ·   \n\n ·  `` · a ·    · `` |  |
| 31 |   \n\n ·    · <|endoftext|> · \n\n ·  \n\n ·    \n\n ·   \n ·     ·   \n\n\n · \n\n\n\n |  |
| 35 | <|endoftext|> · \n\n ·   \n\n · \n\n\n\n · \n\n\n ·    · <|im_end|> ·  […] ·  \n\n ·  \xa0 |  |
| 39 | <|endoftext|> · \n\n · <|im_end|> ·  […] ·   \n\n ·  [...] ·    ·  ... · [ ·  \n\n |  |
| 43 | <|im_end|> ·    ·  […] ·   \n\n · <|endoftext|> ·     ·  \xa0 · [ ·       ·         |  |
| 47 |   \n\n ·   \n ·  \n\n · � · &nbsp ·    \n\n ·    \n · \\n ·   \n  \n ·  \n  \n |  |
| 48 |   \n\n ·   \n · � · &nbsp · **! ·  whispered · \xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0 ·  angels ·   \n    \n ·    \n\n |  |
| 50 | *” · ((* · \xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0 · **! · ▪ ·  whispered · ∙ · ugas · 嬛 · utores |  |
| 51 |  TWO · _two · 两位 · 两只 ·  two ·  zwei · 两名 · two · .two · 两个 |  |
| 55 |  two ·  TWO · two · _two ·  zwei · 两个 · .two ·  Two ·  deux · -two |  |
| 59 |  two · two ·  birds · _two ·  Two ·  TWO · Two · -two ·  deux · .two |  |
| 62 |  two · two ·  Two ·  birds ·  TWO · _two · -two ·  watched ·  deux · Two |  |

## controlled|maintain|lake|C3  (user text: `Here is the word "lake". Keep that word in mind while you copy the following text exactly,…`)

| layer | top-10 at the middle interior token | rank of X over window L24-59 (min / median) |
|---|---|---|
| 23 |  , ·  ; ·  and ·  -- ·  ` ·  & ·  . ·  on ·  in ·  subsequently | 2693 / 144375 |
| 31 |  __ ·  ____ ·  , ·  ... ·  _ ·  ___ ·  . ·  ______ ·  & ·  < | 4033 / 38735 |
| 35 |  , ·    ·  and ·  ， ·  、 · <|endoftext|> · ， ·      ·     ·  \n\n\n | 1643 / 77851 |
| 39 | ， ·  ， ·  、 ·  , · 、 · 和 ·  .** · <|endoftext|> ·  （ ·  ‘ | 107 / 99707 |
| 43 | ， · 、 · 。\\ · ;\\ ·  ， ·  、 · 和 · ； · ,\\ ·      | 50 / 53763 |
| 47 |  , · ,** · ， · ,\\ · ､ ·  **, · , ·  [, · ;\\ · 、 | 151 / 24438 |
| 48 | ,count · ､ · ,ID · ,list · ,msg · ｀ · ,double · ,array ·  verifying · ,id | 180 / 65001 |
| 50 | ,list · ;** · [,] · ,msg · ambat · ,ID · 、 · ,count · ， · plusplus | 3306 / 135696 |
| 51 | checked · _checked ·  checked · -checked · /check · 核对 · 、 · ， ·  inspected · ached | 132 / 83154 |
| 55 |  checked · checked · -checked ·  Checked · _checked · Checked · .checked ·  inspected · 检查 ·  verified | 14 / 52386 |
| 59 |  checked · checked ·  Checked · -checked · Checked · _checked · 检查 · .checked ·  checking ·  CHECK | 3 / 1521 |
| 62 | , ·  checked · checked ·  Checked · -checked · Checked · ,, ·  , · .checked · _checked | 2 / 403 |

## controlled|mention|lake|C3  (user text: `Here is the word "lake". That word occurs one time. Now copy the following text exactly, w…`)

| layer | top-10 at the middle interior token | rank of X over window L24-59 (min / median) |
|---|---|---|
| 23 |  , ·  ; ·  and ·  -- ·  ` ·  . ·  & ·  in ·  on ·  ' | 7758 / 141733 |
| 31 |  __ ·  , ·  ... ·  ____ ·  ___ ·  _ ·  < ·  . ·  & ·    | 3719 / 48881 |
| 35 |  , ·    · <|endoftext|> ·  ， · ， ·  and ·  、 ·      ·     ·  \n\n\n | 1218 / 107809 |
| 39 | ， ·  ， · 、 ·  、 · <|endoftext|> ·  , · 和 · <|im_end|> · ； · 。\\ | 176 / 125046 |
| 43 | ， · 、 · 。\\ ·  ， · ;\\ · ； · 和 ·  、 · ,\\ ·  [, | 156 / 76633 |
| 47 |  , · ,\\ · ， · , · ;\\ · [,] ·   \n\n · ､ ·  inspect · 、 | 135 / 21415 |
| 48 | ,count · ,list · ,ID · ､ · ,double · [,] · ｀ · ,msg · ,array · inspect | 295 / 77522 |
| 50 | ,list · [,] · ,count · ;** · ,msg · ,string · 、 · ,ID · ,json · ， | 12251 / 178152 |
| 51 | checked · _checked · -checked ·  checked · ,count · /check · 核对 · ， · 、 · 查验 | 3670 / 127496 |
| 55 |  checked · checked · -checked ·  Checked · _checked · Checked · .checked ·  inspected ·  verified · 检查 | 47 / 65965 |
| 59 |  checked · checked ·  Checked · -checked · Checked · _checked · 检查 · .checked ·  checking ·  CHECK | 31 / 2303 |
| 62 | , ·  checked · checked ·  Checked · -checked · Checked ·  , · ,, · .checked · _checked | 11 / 588 |

## controlled|mention|river|C2  (user text: `Here is the word "river". That word occurs one time. Now copy the following text exactly, …`)

| layer | top-10 at the middle interior token | rank of X over window L24-59 (min / median) |
|---|---|---|
| 23 | \n\n · <|endoftext|> · \n\n\n\n · \n\n\n ·   \n\n · a ·    · s ·  • ·  `` | 11173 / 59277 |
| 31 |   \n\n ·    · <|endoftext|> · \n\n ·  \n\n ·    \n\n · \n\n\n\n ·     ·   \n ·   \n\n\n | 9131 / 27432 |
| 35 | <|endoftext|> · \n\n ·    · \n\n\n\n ·   \n\n · \n\n\n ·  ... · <|im_end|> ·  • ·  […] | 16740 / 51977 |
| 39 | <|endoftext|> · \n\n · <|im_end|> ·   \n\n ·    ·  […] ·  \n\n · \n\n\n\n · \n\n\n ·  ... | 122 / 72391 |
| 43 | <|im_end|> ·    ·     ·   \n\n ·      ·        · <|endoftext|> ·       ·         ·          | 194 / 20681 |
| 47 |  two ·   \n\n ·  TWO ·   \n ·  Two ·  five · � ·  \n\n · <|im_end|> ·  three | 298 / 6239 |
| 48 |  TWO · 两只 ·   \n\n ·  two · **! ·  dua · &nbsp ·  zwei · two ·  twins | 1118 / 56155 |
| 50 | ((* · **! · 两只 · 两位 · \xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0 · *” ·  اثنين ·  zwei · ух · 那两个 | 11972 / 169251 |
| 51 |  TWO ·  zwei · _two · 两只 ·  two · two · 两位 · .two · สอง ·  deux | 7667 / 35856 |
| 55 |  two · two ·  TWO · _two ·  zwei · .two ·  deux ·  Two · 两个 · Two | 804 / 10018 |
| 59 |  two ·  birds · two · _two ·  Two · birds · Two ·  Birds ·  TWO ·  deux | 69 / 597 |
| 62 |  two · two ·  birds ·  Two · _two ·  TWO ·  deux · -two · Two ·  zwei | 18 / 267 |

## controlled|plain_mention|rug|C2  (user text: `rug. Now copy the following text exactly, word for word:

Dust settled slowly over the vil…`)

| layer | top-10 at the middle interior token | rank of X over window L24-59 (min / median) |
|---|---|---|
| 23 | \n\n · \n\n\n · \n\n\n\n ·   \n\n · <|endoftext|> ·  • ·    · a ·  `` ·   \n | 8859 / 43112 |
| 31 |   \n\n ·    · <|endoftext|> ·  \n\n · \n\n ·   \n ·    \n\n · <|im_end|> ·   \n\n\n · \n\n\n\n | 12625 / 22470 |
| 35 | <|endoftext|> · \n\n ·   \n\n · \n\n\n\n · \n\n\n · <|im_end|> ·  \n\n ·    ·  […] ·  ... | 38983 / 88013 |
| 39 | <|endoftext|> · \n\n · <|im_end|> ·  […] ·   \n\n ·  [...] ·  \n\n ·  ... · ... ·    | 38513 / 67132 |
| 43 | <|im_end|> · <|endoftext|> ·   \n\n · [ ·    ·  […] · \n\n ·     · &nbsp ·   \n | 29395 / 57617 |
| 47 |   \n\n ·   \n ·  \n\n · &nbsp · � · <|im_end|> ·  women · **! ·    \n\n ·  men | 10072 / 29339 |
| 48 |   \n\n · **! · &nbsp · � · <|im_end|> ·  angels · !** ·   \n · **” ·  whispered | 6078 / 24917 |
| 50 | *” · ((* · **! · !* · ▪ · %X · 星人 · • · \xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0 · !** | 14505 / 67427 |
| 51 |  TWO · 两位 · 两只 · _two ·  zwei · two ·  two · 两个 · 两名 ·  두 | 5109 / 27547 |
| 55 |  two · two ·  TWO · _two ·  zwei · 两个 ·  Two ·  deux · Two · .two | 8528 / 35272 |
| 59 |  two · two ·  birds · _two ·  Two ·  TWO · Two · birds ·  deux · 两只 | 767 / 10014 |
| 62 |  two · two ·  Two ·  birds ·  TWO · _two · -two ·  deux · Two ·  watched | 436 / 2170 |

## controlled|never_think|cup|C2  (user text: `Here is the word "cup". Never think about that word. Now copy the following text exactly, …`)

| layer | top-10 at the middle interior token | rank of X over window L24-59 (min / median) |
|---|---|---|
| 23 | \n\n · \n\n\n\n · \n\n\n · <|endoftext|> ·   \n\n · a ·    ·  • ·  `` · s | 2822 / 24139 |
| 31 |   \n\n · <|endoftext|> · \n\n ·    ·  \n\n ·    \n\n · \n\n\n\n ·   \n ·   \n\n\n · <|im_end|> | 3714 / 17576 |
| 35 | <|endoftext|> · \n\n · \n\n\n\n ·   \n\n · <|im_end|> · \n\n\n ·  \n\n ·    ·  ... ·    \n\n | 8367 / 71811 |
| 39 | <|endoftext|> · \n\n · <|im_end|> ·   \n\n ·  \n\n · \n\n\n\n ·  […] ·  [...] ·  ... · \n\n\n | 11088 / 128073 |
| 43 | <|im_end|> ·   \n\n · <|endoftext|> ·    · \n\n · \n\n\n\n ·   \n\n\n ·     ·    \n\n · [ | 10057 / 107729 |
| 47 |   \n\n ·   \n ·  \n\n · <|im_end|> · � · &nbsp ·   \n  \n ·    \n\n ·  \n  \n · **! | 2013 / 13830 |
| 48 |   \n\n · **! · <|im_end|> · &nbsp ·   \n ·   \n  \n · � · **” ·    \n\n ·  \n\n | 6322 / 38032 |
| 50 | **! · ((* · *” · ▪ · !** · [${ · !* · %X · **” · *[ | 27290 / 101437 |
| 51 | 两位 · _two ·  zwei ·  TWO · 两只 · two ·  two · 两名 · 两个 ·  두 | 3681 / 38474 |
| 55 |  two · two · _two ·  TWO ·  zwei · 两个 ·  Two ·  deux · .two · Two | 1594 / 26738 |
| 59 |  two · two ·  birds · _two ·  Two · Two ·  deux ·  TWO · -two · birds | 274 / 3328 |
| 62 |  two · two ·  Two ·  birds · _two · -two ·  TWO ·  deux · Two ·  zwei | 73 / 378 |

## controlled|mention|airport|C3  (user text: `Here is the word "airport". That word occurs one time. Now copy the following text exactly…`)

| layer | top-10 at the middle interior token | rank of X over window L24-59 (min / median) |
|---|---|---|
| 23 |  , ·  ; ·  and ·  -- ·  ` ·  . ·  & ·  in ·  on ·  subsequently | 3839 / 144286 |
| 31 |  __ ·  ____ ·  ... ·  , ·  ___ ·  _ ·  ______ ·  < ·  & ·  . | 1506 / 14824 |
| 35 |  , ·    · <|endoftext|> ·  ， ·      · ， ·  and ·  、 ·     ·  \n\n\n | 325 / 63624 |
| 39 | ， ·  ， · 、 ·  、 ·  , · <|endoftext|> · 和 · <|im_end|> · ； ·    | 61 / 77813 |
| 43 | ， · 、 · 。\\ ·  ， · ;\\ ·  、 · ,\\ · ； · 和 ·  [, | 57 / 21480 |
| 47 |  , · ,\\ · ， · , · ;\\ · [,] · ,** ·  inspect · ､ · 、 | 104 / 25181 |
| 48 | ,count · ,list · ,ID · ､ · ,double · [,] · ｀ · ,array · ,msg · inspect | 151 / 95550 |
| 50 | ,list · ,count · [,] · ;** · ,string · 、 · ,msg · ,ID · %X · ， | 220 / 145450 |
| 51 | checked · _checked ·  checked · -checked · ,count · /check · 核对 · 查验 · ， · 、 | 2 / 107682 |
| 55 |  checked · checked · -checked ·  Checked · _checked · Checked · .checked ·  inspected · 检查 ·  verified | 10 / 45414 |
| 59 |  checked · checked ·  Checked · -checked · Checked · _checked · 检查 · .checked ·  checking ·  CHECK | 22 / 4764 |
| 62 | , ·  checked · checked ·  Checked · -checked · Checked · ,, ·  , · .checked · _checked | 4 / 1577 |

## controlled|mention|silver|C3  (user text: `Here is the word "silver". That word occurs one time. Now copy the following text exactly,…`)

| layer | top-10 at the middle interior token | rank of X over window L24-59 (min / median) |
|---|---|---|
| 23 |  , ·  ; ·  and ·  -- ·  ` ·  . ·  & ·  on ·  in ·  subsequently | 1105 / 28703 |
| 31 |  __ ·  ____ ·  , ·  ___ ·  ... ·  _ ·  ______ ·  < ·  . ·  ________ | 1111 / 8072 |
| 35 |  , · <|endoftext|> ·    ·      ·  ， ·  and · ， ·  、 ·     ·  \n\n\n | 421 / 44570 |
| 39 | ， ·  ， · <|endoftext|> · 、 ·  、 ·  , · 和 · <|im_end|> ·    ·  \r\n\r\n | 45 / 49076 |
| 43 | ， · 、 · 。\\ · ;\\ ·  ， · <|im_end|> ·  、 · ,\\ · ； ·      | 88 / 35409 |
| 47 |  , · ,\\ · ， · , · ;\\ ·   \n\n · ､ · [,] ·  inspect · ,** | 115 / 9918 |
| 48 | ,count · ,list · ,ID · ､ · ,double · ｀ · [,] · ,msg · ,array · 稳增长 | 397 / 79141 |
| 50 | ,list · [,] · ,count · ;** · ,msg · ,string · ,ID · ambat · 、 · plusplus | 7188 / 189635 |
| 51 | checked · _checked · -checked ·  checked · ,count · /check · 核对 · 查验 · 、 · ， | 275 / 131626 |
| 55 |  checked · checked · -checked ·  Checked · _checked · Checked · .checked ·  inspected ·  verified · 检查 | 114 / 148678 |
| 59 |  checked · checked ·  Checked · -checked · Checked · _checked · 检查 · .checked ·  checking ·  CHECK | 12 / 20992 |
| 62 | , ·  checked · checked ·  Checked · -checked · Checked ·  , · ,, · .checked · _checked | 4 / 973 |

## controlled|plain_mention|bubble|C3  (user text: `bubble. Now copy the following text exactly, word for word:

Several boxes of files were m…`)

| layer | top-10 at the middle interior token | rank of X over window L24-59 (min / median) |
|---|---|---|
| 23 |  , ·  ; ·  and ·  -- ·  & ·  ` ·  on ·  . ·  subsequently ·  in | 475 / 115945 |
| 31 |  ____ ·  __ ·  ___ ·  ______ · <|im_end|> · ____ ·  _ ·  ________ ·  _____ ·  \n\n | 2925 / 34693 |
| 35 | <|endoftext|> ·  , ·  and ·    · \xa0 ·  \n\n ·  \n\n\n ·      ·  ， ·     | 2833 / 135343 |
| 39 | <|endoftext|> ·  , ·  ， · ， ·  、 · <|im_end|> ·  \n\n · 、 ·   \n\n ·  ‘ | 589 / 103544 |
| 43 | ， · 、 ·  ， · <|im_end|> ·   \n\n · 。\\ · ； · ;\\ ·  , ·    | 519 / 92813 |
| 47 |  , · , · ､ · ,** · ， ·  [, ·  **, · [, · ,\\ ·  、 | 521 / 120275 |
| 48 | ､ · ,count · ,ID · ,double · [,] · ｀ · ,list · ,msg · , · [, | 292 / 109584 |
| 50 | 、 · ， · [,] · ,list · ;** · [], · ,ID · ,string · ,msg · ,count | 516 / 189332 |
| 51 | 、 · checked · ， · , · -checked · _checked ·  checked · /check · [], · ,count | 7 / 177003 |
| 55 |  checked · checked · -checked ·  Checked · Checked · _checked · .checked ·  inspected · 检查 · :checked | 1 / 83937 |
| 59 |  checked · checked ·  Checked · -checked · Checked · _checked · 检查 · .checked ·  checking ·  CHECK | 11 / 1852 |
| 62 | , ·  checked · checked ·  Checked · -checked · ,, · Checked ·  , · .checked · ， | 4 / 454 |
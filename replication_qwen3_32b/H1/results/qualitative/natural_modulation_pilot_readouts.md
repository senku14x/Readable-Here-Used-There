# Natural modulation — qualitative readouts (J_NP top-10, interior carrier positions)

Teacher-forced text: the assistant turn is the carrier copied verbatim; nothing is generated. Position shown = middle interior token. Ranks are over the full 248k vocabulary. Selection: the fixed cells listed in `meta.json.topk_cells` plus a seeded random sample (`qual_random_cells`, seed 20260907).


## controlled|maintain|orange|C0  (user text: `Here is the word "orange". Keep that word in mind while you copy the following text exactl…`)

| layer | top-10 at the middle interior token | rank of X over window L24-59 (min / median) |
|---|---|---|
| 23 |  ... ·  . ·  new ·  .\n ·  cities ·  [...] ·  ...\n ·  towns ·  equipment ·  .... | 2441 / 13063 |
| 31 |  .\n ·  new ·  _ ·  cities ·  programs ·  areas ·  . ·  equipment ·  towns ·  services | 1415 / 6129 |
| 35 |  .\n ·  . ·  new ·  ... ·  areas ·  .\n\n ·  projects ·  cities ·  programs ·  careers | 1658 / 8993 |
| 39 |  .\n ·  . ·  programs ·  projects ·  new ·  plans ·  areas ·  missions ·  _ ·  cities | 523 / 4263 |
| 43 |  _ ·  . ·  _. · . · .\n ·  [ ·  ** ·  projects ·  New ·  .\n | 1804 / 6089 |
| 47 | \xa0 · 产业园区 · \\n · .\\ · , · .</ · ," · 产业园 · . · .\n | 450 / 8727 |
| 48 | \xa0 · , · .\n · 产业园区 ·  \n · . · .\\ · ," · .</ · Â | 284 / 6964 |
| 50 | \xa0 · 产业园区 ·  \n · 产业园 · .\\ · благо · 政策措施 · 工作任务 · 公益性 · 人居环境 | 1106 / 8069 |
| 51 | благо · 产业园区 · schlü · 炕 · 人居环境 · естественн ·  Geile · индивид · реги · практик | 9056 / 37051 |
| 55 |  community · 社區 ·  communities · 社区 ·  Community · -community · /community · Community ·  comunidad · .community | 7039 / 31003 |
| 59 |  community · 社区 · 社區 ·  Community · community · Community · -community · .community · コミュニ · _community | 1355 / 8454 |
| 62 |  community · 社区 · 社區 ·  Community · community · .community · -community ·  communauté · コミュニ ·  comunidad | 16 / 228 |

## controlled|mention|orange|C0  (user text: `Here is the word "orange". That word occurs one time. Now copy the following text exactly,…`)

| layer | top-10 at the middle interior token | rank of X over window L24-59 (min / median) |
|---|---|---|
| 23 |  ... ·  . ·  .\n ·  new ·  [...] ·  ...\n ·  cities ·  towns ·  .... ·  equipment | 2524 / 10761 |
| 31 |  .\n ·  new ·  _ ·  cities ·  . ·  areas ·  programs ·  equipment ·  towns ·  services | 1293 / 7622 |
| 35 |  .\n ·  . ·  new ·  ... ·  areas ·  .\n\n ·  cities ·  projects ·  programs ·  careers | 1617 / 8550 |
| 39 |  .\n ·  . ·  programs ·  new ·  projects ·  plans ·  areas ·  missions ·  cities ·  offices | 526 / 4720 |
| 43 |  _ ·  . · . ·  _. ·  \n · .\n ·  ** ·  [ ·  ... ·  projects | 1884 / 7335 |
| 47 | \xa0 · 产业园区 · .\\ · , · \\n · . ·  \n · 产业园 · .$. · .</ | 637 / 17418 |
| 48 | \xa0 · , · .\n · 产业园区 ·  \n · . · .\\ · .</ · ; · ," | 658 / 13259 |
| 50 | \xa0 · 产业园区 · .\\ · 产业园 · \xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0 · 政策措施 ·  \n · благо · .</ · 科技园 | 1809 / 10704 |
| 51 | благо · 产业园区 · 人居环境 · \xa0 ·  Geile · 炕 · естественн · индивид · практик · реги | 8305 / 53296 |
| 55 |  community · 社區 ·  communities · 社区 ·  Community · -community · /community ·  comunidad · コミュニ · 产业园区 | 2566 / 39186 |
| 59 |  community · 社区 · 社區 ·  Community · community · Community · -community · .community · コミュニ · _community | 1003 / 10411 |
| 62 |  community · 社区 · 社區 ·  Community · community · .community · -community · コミュニ ·  communauté ·  comunidad | 20 / 243 |

## controlled|plain_mention|orange|C0  (user text: `orange. Now copy the following text exactly, word for word:

The committee reviewed the an…`)

| layer | top-10 at the middle interior token | rank of X over window L24-59 (min / median) |
|---|---|---|
| 23 |  ... ·  . ·  new ·  .\n ·  cities ·  towns ·  equipment ·  programs ·  areas ·  ...\n | 2385 / 13060 |
| 31 |  .\n ·  new ·  programs ·  equipment ·  cities ·  areas ·  developments ·  services ·  towns ·  projects | 1439 / 8342 |
| 35 |  .\n ·  new ·  . ·  projects ·  programs ·  areas ·  ... · .\n ·  .\n\n ·  cities | 2312 / 8952 |
| 39 |  .\n ·  programs ·  projects ·  . ·  new ·  plans ·  areas ·  funding ·  missions ·  _ | 770 / 6010 |
| 43 |  _ ·  . ·  projects ·  ... ·  _. ·  \n ·  programs · .\n · . ·  new | 2289 / 7875 |
| 47 | \xa0 · 产业园区 · , · . · .\\ · � · .\n · .</ · ." · ," | 3957 / 22697 |
| 48 | \xa0 · , · .\n · 产业园区 · . ·  \n · .\\ · .</ · � · ," | 8852 / 25380 |
| 50 | \xa0 · 产业园区 · \xa0\xa0 · \xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0 · \xa0\xa0\xa0\xa0\xa0\xa0\xa0 · 产业园 · � · 公益性 · \xa0\xa0\xa0 · , | 4792 / 26806 |
| 51 | благо · 产业园区 · \xa0 · естественн · 炕 · реги · индивид · 人居环境 · 村镇 · \xa0\xa0\xa0\xa0\xa0\xa0\xa0 | 21134 / 79900 |
| 55 |  community · 社區 · 社区 ·  communities · -community ·  Community · /community · コミュニ · Community · 产业园区 | 7098 / 52960 |
| 59 |  community · 社区 · 社區 ·  Community · community · Community · -community · .community · コミュニ · /community | 4070 / 16375 |
| 62 |  community · 社区 ·  Community · 社區 · community · .community · -community · コミュニ ·  communauté ·  comunidad | 37 / 669 |

## controlled|absent|NONE|C0  (user text: `A single passage of text is given below. Now copy the following text exactly, word for wor…`)

| layer | top-10 at the middle interior token | rank of X over window L24-59 (min / median) |
|---|---|---|
| 23 |  ... ·  . ·  .\n ·  new ·  cities ·  ...\n ·  towns ·  equipment ·  [...] ·  areas |  |
| 31 |  .\n ·  new ·  programs ·  equipment ·  _ ·  cities ·  areas ·  towns ·  services ·  developments |  |
| 35 |  .\n ·  new ·  . ·  projects ·  ... ·  areas ·  programs ·  .\n\n · .\n ·  cities |  |
| 39 |  .\n ·  programs ·  projects ·  . ·  new ·  plans ·  areas ·  missions ·  _ ·  activities |  |
| 43 |  . ·  _ ·  ... ·  \n · . ·  projects · .\n ·  _. ·  .\n ·  programs |  |
| 47 | \xa0 · 产业园区 · , · . · � · .\\ · .\n · ," · ." · 产业园 |  |
| 48 | \xa0 · , · .\n · 产业园区 ·  \n · . · .\\ · � · .</ · ," |  |
| 50 | \xa0 · 产业园区 · 产业园 · \xa0\xa0 · \xa0\xa0\xa0\xa0\xa0\xa0\xa0 · \xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0 · \xa0\xa0\xa0 · 公益性 · 政策措施 · 目标任务 |  |
| 51 | 产业园区 · благо · \xa0 · естественн · 人居环境 · 炕 ·  Geile · реги · 产业园 · 发展空间 |  |
| 55 |  community · 社區 · 社区 ·  communities · -community ·  Community · /community · Community ·  comunidad · コミュニ |  |
| 59 |  community · 社区 · 社區 ·  Community · community · Community · -community · .community · コミュニ · _community |  |
| 62 |  community · 社区 ·  Community · 社區 · community · .community · -community · コミュニ ·  comunidad ·  communauté |  |

## controlled|maintain|castle|C1  (user text: `Here is the word "castle". Keep that word in mind while you copy the following text exactl…`)

| layer | top-10 at the middle interior token | rank of X over window L24-59 (min / median) |
|---|---|---|
| 23 |  . ·  .\n · \xa0 ·  .\n\n · .\n · . ·  _ · .\n\n · ...\n · ._ | 218 / 4709 |
| 31 |  .\n ·  .\n\n ·  . ·  _ · .\n ·  in · \xa0 ·  with ·  on · ...\n | 56 / 1382 |
| 35 | .\n\n · .\n ·  .\n\n ·  .\n · . ·  . ·  in ·  _ ·  on ·  with | 131 / 2919 |
| 39 |  .\n ·  . · .\n ·  _ ·  in ·  .\n\n ·  on ·  with · . ·  as | 269 / 2650 |
| 43 | . ·  . ·  _ ·  _. · .\n · , ·  , ·  .\n ·  in ·  and | 870 / 6625 |
| 47 | \xa0 · , · . · ; · � · schlü · \xa0\xa0 · 讫 · 居室 · \xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0 | 182 / 21755 |
| 48 | \xa0 · , · . · \xa0\xa0 · ; · .\n · \xa0\n · \xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0 · � · \xa0\xa0\xa0 | 758 / 22481 |
| 50 | \xa0 · 人居环境 · schlü · 自然而 · 在过渡 · \xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0 · 다가 · \xa0\xa0 · \xa0\xa0\xa0\xa0\xa0\xa0\xa0 · 寄せ | 1786 / 70663 |
| 51 | schlü ·  Geile · 人居环境 ·  Erotische · 在过渡 · 自然而 · AndGet · 停下来 · 行政部门 · 寄せ | 7888 / 105517 |
| 55 | 並且 ·  and · 而且还 · 而且 · AndView ·  และ · AndGet ·  그리고 · 并且 ·  và | 4601 / 77939 |
| 59 |  and ·  And · , · ,and ·  และ · And · .and ·  AND · _AND · —and | 171 / 18452 |
| 62 | , ·  and ·  , · . · ,\n · ,and · ,\n\n · ,** · ; · ., | 17 / 1523 |

## controlled|mention|castle|C1  (user text: `Here is the word "castle". That word occurs one time. Now copy the following text exactly,…`)

| layer | top-10 at the middle interior token | rank of X over window L24-59 (min / median) |
|---|---|---|
| 23 |  . ·  .\n ·  .\n\n · \xa0 · .\n · . · ...\n ·  _ · .\n\n ·  in | 200 / 4285 |
| 31 |  .\n ·  .\n\n ·  . ·  _ ·  in · .\n · \xa0 ·  with · ...\n ·  on | 12 / 1456 |
| 35 | .\n\n · .\n ·  .\n\n ·  .\n · . ·  . ·  in ·  with ·  _ ·  on | 6 / 2967 |
| 39 |  . ·  .\n · .\n ·  in ·  _ ·  .\n\n ·  on ·  with ·  as · . | 5 / 2721 |
| 43 | . ·  . · .\n ·  _ ·  _. ·  .\n · , ·  , ·  in ·  and | 170 / 8097 |
| 47 | \xa0 · , · . · ; · schlü · � · \xa0\xa0 · 家喻户晓 · \xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0 · 人居环境 | 289 / 31340 |
| 48 | \xa0 · , · . · ; · \xa0\xa0 · .\n · \xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0 · \xa0\n · � · \xa0\xa0\xa0 | 500 / 30111 |
| 50 | \xa0 · 人居环境 · schlü · 自然而 · 如期 · \xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0 · \xa0\xa0\xa0\xa0\xa0\xa0\xa0 · 다가 · 在过渡 · \xa0\xa0 | 919 / 75026 |
| 51 | schlü ·  Geile · 人居环境 ·  Erotische · 自然而 · AndGet · 汽车产业 · 在过渡 · AndView · 如期 | 4750 / 100948 |
| 55 | 並且 ·  and · 而且还 · 而且 · AndView · AndGet ·  และ ·  그리고 · 并且 ·  và | 2922 / 57347 |
| 59 |  and ·  And · , · ,and ·  และ · .and ·  AND · _AND · _and · And | 2 / 18156 |
| 62 | , ·  and ·  , · . · ,\n · ,** · ., · ,\\ · ; · ,and | 4 / 925 |

## controlled|mention|diamond|C0  (user text: `Here is the word "diamond". That word occurs one time. Now copy the following text exactly…`)

| layer | top-10 at the middle interior token | rank of X over window L24-59 (min / median) |
|---|---|---|
| 23 |  ... ·  . ·  .\n ·  new ·  ...\n ·  [...] ·  cities ·  towns ·  .... ·  equipment | 4522 / 30758 |
| 31 |  .\n ·  new ·  cities ·  _ ·  programs ·  areas ·  . ·  equipment ·  towns ·  services | 12838 / 40766 |
| 35 |  .\n ·  . ·  new ·  ... ·  areas ·  .\n\n ·  projects ·  cities ·  programs ·  careers | 5848 / 25198 |
| 39 |  .\n ·  . ·  programs ·  projects ·  new ·  plans ·  areas ·  missions ·  cities ·  _ | 5391 / 19795 |
| 43 |  _ ·  . ·  _. ·  \n · . ·  ** ·  ... ·  projects · .\n ·  programs | 4585 / 23997 |
| 47 | \xa0 · 产业园区 · .\\ · \\n · , · .$. · 产业园 · .</ · \xa0\xa0\xa0 · . | 32153 / 84884 |
| 48 | \xa0 · , · 产业园区 ·  \n · .\n · .\\ · . · .</ · ," · \\n | 18707 / 71701 |
| 50 | \xa0 · 产业园区 · .\\ · 产业园 · \xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0 · \xa0\xa0\xa0\xa0\xa0\xa0\xa0 · 公益性 · 政策措施 · \xa0\xa0\xa0 · благо | 16418 / 77846 |
| 51 | благо · 产业园区 · 人居环境 · \xa0 · индивид · естественн · 炕 · реги · практик ·  Geile | 57493 / 116754 |
| 55 |  community · 社區 · 社区 ·  communities ·  Community · -community · /community · コミュニ ·  comunidad · Community | 3 / 89874 |
| 59 |  community · 社区 · 社區 ·  Community · community · Community · -community · .community · コミュニ · _community | 38 / 47746 |
| 62 |  community · 社区 · 社區 ·  Community · community · .community · コミュニ · -community ·  comunidad ·  communauté | 14 / 149 |

## controlled|plain_mention|tiger|C0  (user text: `tiger. Now copy the following text exactly, word for word:

The committee reviewed the ann…`)

| layer | top-10 at the middle interior token | rank of X over window L24-59 (min / median) |
|---|---|---|
| 23 |  ... ·  . ·  new ·  .\n ·  cities ·  towns ·  equipment ·  areas ·  programs ·  ...\n | 5290 / 18268 |
| 31 |  new ·  .\n ·  programs ·  cities ·  equipment ·  areas ·  _ ·  developments ·  towns ·  services | 4521 / 21525 |
| 35 |  .\n ·  new ·  . ·  projects ·  programs ·  areas ·  ... ·  .\n\n ·  cities ·  missions | 6049 / 14067 |
| 39 |  .\n ·  programs ·  projects ·  . ·  new ·  plans ·  areas ·  funding ·  _ ·  missions | 10284 / 16618 |
| 43 |  _ ·  . ·  projects ·  _. ·  ... ·  \n ·  programs · . · .\n ·  new | 6199 / 16162 |
| 47 | \xa0 · 产业园区 · , · . · � · .\\ · .\n · ," · .</ · ." | 18091 / 94163 |
| 48 | \xa0 · , · .\n · 产业园区 · . ·  \n · .</ · � · .\\ · ," | 21747 / 77809 |
| 50 | \xa0 · 产业园区 · \xa0\xa0 · \xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0 · \xa0\xa0\xa0\xa0\xa0\xa0\xa0 · � · \xa0\xa0\xa0 · 产业园 · 公益性 · , | 17214 / 46485 |
| 51 | благо · 产业园区 · \xa0 · естественн · 炕 · 人居环境 · реги · \xa0\xa0\xa0\xa0\xa0\xa0\xa0 · индивид · 村镇 | 39886 / 92461 |
| 55 |  community · 社區 · 社区 ·  communities · -community ·  Community · /community · コミュニ · 产业园区 · Community | 10487 / 58050 |
| 59 |  community · 社区 · 社區 ·  Community · community · Community · -community · .community · コミュニ · _community | 4995 / 33962 |
| 62 |  community · 社区 · 社區 ·  Community · community · .community · コミュニ · -community ·  communauté ·  comunidad | 78 / 698 |

## controlled|never_think|castle|C0  (user text: `Here is the word "castle". Never think about that word. Now copy the following text exactl…`)

| layer | top-10 at the middle interior token | rank of X over window L24-59 (min / median) |
|---|---|---|
| 23 |  ... ·  . ·  new ·  .\n ·  cities ·  ...\n ·  towns ·  equipment ·  [...] ·  areas | 271 / 15549 |
| 31 |  .\n ·  new ·  programs ·  cities ·  areas ·  equipment ·  _ ·  . ·  towns ·  developments | 115 / 6107 |
| 35 |  .\n ·  . ·  new ·  ... ·  areas ·  projects ·  programs ·  .\n\n ·  cities ·  missions | 247 / 8306 |
| 39 |  .\n ·  . ·  programs ·  projects ·  new ·  plans ·  areas ·  missions ·  cities ·  _ | 778 / 8532 |
| 43 |  _ ·  . ·  _. ·  projects ·  \n · . ·  programs · .\n ·  ... ·  activities | 3098 / 16170 |
| 47 | \xa0 · 产业园区 · \\n · .\\ · , · .</ ·  \n · ," · . · 产业园 | 7693 / 64145 |
| 48 | \xa0 · 产业园区 · , ·  \n · .\n · .</ · .\\ · . · ," · \\n | 14772 / 72674 |
| 50 | 产业园区 · \xa0 · 公益性 · 人居环境 · 产业园 · благо · .\\ · \xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0 · .</ · 政策措施 | 11154 / 82348 |
| 51 | благо · 产业园区 · естественн · 人居环境 · реги · 炕 · индивид ·  Geile · \xa0 · 村镇 | 46696 / 113923 |
| 55 |  community · 社區 · 社区 ·  communities · -community ·  Community · /community ·  comunidad · Community · コミュニ | 1903 / 103806 |
| 59 |  community · 社区 · 社區 · community ·  Community · Community · -community · .community · コミュニ · _community | 1234 / 42892 |
| 62 |  community · 社区 ·  Community · 社區 · community · .community · -community ·  communauté · コミュニ ·  comunidad | 39 / 4173 |

## controlled|mention|guitar|C1  (user text: `Here is the word "guitar". That word occurs one time. Now copy the following text exactly,…`)

| layer | top-10 at the middle interior token | rank of X over window L24-59 (min / median) |
|---|---|---|
| 23 |  . ·  .\n · \xa0 ·  .\n\n · .\n · . ·  _ · ...\n · .\n\n · ._ | 302 / 8470 |
| 31 |  .\n ·  .\n\n ·  . ·  _ · .\n ·  in · \xa0 ·  with · ...\n ·  on | 69 / 4959 |
| 35 | .\n · .\n\n ·  .\n\n ·  .\n · . ·  . ·  in ·  with ·  _ ·  on | 11 / 6357 |
| 39 |  . ·  .\n · .\n ·  _ ·  in ·  .\n\n ·  on ·  with ·  as · . | 3 / 5799 |
| 43 | . ·  . · .\n ·  _ ·  _. ·  .\n · , ·  , ·  in ·  and | 9 / 5403 |
| 47 | \xa0 · , · . · ; · schlü · � · \xa0\xa0 · 家喻户晓 · \xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0 · 居室 | 792 / 35749 |
| 48 | \xa0 · , · . · ; · \xa0\xa0 · .\n · \xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0 · � · \xa0\n · \xa0\xa0\xa0 | 161 / 33595 |
| 50 | \xa0 · schlü · 人居环境 · 如期 · 自然而 · \xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0 ·  Geile · \xa0\xa0\xa0\xa0\xa0\xa0\xa0 · 在过渡 · 汽车产业 | 4778 / 37491 |
| 51 | schlü ·  Geile · 人居环境 ·  Erotische · 自然而 · 汽车产业 · 在过渡 · AndGet · 逡 · 如期 | 7541 / 81166 |
| 55 | 並且 ·  and · 而且还 · 而且 · AndView · AndGet ·  และ ·  그리고 · 并且 ·  và | 7 / 57440 |
| 59 |  and ·  And · , · ,and ·  และ ·  AND · .and · _AND ·  , · And | 2 / 25340 |
| 62 | , ·  and · . ·  , · ,\n · ., · ; · ,** · ,\\ · ,and | 31 / 3682 |

## controlled|mention|diamond|C1  (user text: `Here is the word "diamond". That word occurs one time. Now copy the following text exactly…`)

| layer | top-10 at the middle interior token | rank of X over window L24-59 (min / median) |
|---|---|---|
| 23 |  . ·  .\n ·  .\n\n · \xa0 · .\n · . ·  _ · .\n\n · ...\n ·  in | 3197 / 42920 |
| 31 |  .\n ·  .\n\n ·  . ·  _ · .\n ·  in · \xa0 ·  with · ...\n ·  on | 798 / 30143 |
| 35 | .\n · .\n\n ·  .\n\n ·  .\n · . ·  . ·  in ·  with ·  on ·  _ | 35 / 25974 |
| 39 |  . ·  .\n ·  in · .\n ·  _ ·  .\n\n ·  on ·  with ·  as · . | 19 / 17181 |
| 43 | . ·  . · .\n ·  _. ·  _ ·  .\n · , ·  , ·  in ·  and | 215 / 14759 |
| 47 | \xa0 · , · . · ; · schlü · � · \xa0\xa0 · \xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0 · 人居环境 · 家喻户晓 | 11838 / 90871 |
| 48 | \xa0 · , · . · ; · .\n · \xa0\xa0 · \xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0 · � · \xa0\xa0\xa0 · \xa0\n | 6742 / 76961 |
| 50 | \xa0 · 人居环境 · schlü · 如期 · 自然而 · \xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0 · 다가 · \xa0\xa0\xa0\xa0\xa0\xa0\xa0 · 在过渡 · 汽车产业 | 4643 / 82385 |
| 51 | schlü ·  Geile · 人居环境 ·  Erotische · 自然而 · AndGet · 汽车产业 · 在过渡 · 逡 · 如期 | 41384 / 113898 |
| 55 | 並且 ·  and · 而且 · 而且还 · AndView · AndGet ·  และ · 并且 ·  그리고 ·  và | 4 / 107082 |
| 59 |  and ·  And · , · ,and ·  และ · .and ·  AND · _AND · And · _and | 2 / 70231 |
| 62 | , ·  and · . ·  , · ,\n · ., · ,** · ; · ,\\ · ,and | 4 / 1779 |

## controlled|plain_mention|orange|C1  (user text: `orange. Now copy the following text exactly, word for word:

After a brief announcement th…`)

| layer | top-10 at the middle interior token | rank of X over window L24-59 (min / median) |
|---|---|---|
| 23 |  . ·  .\n ·  .\n\n · \xa0 · .\n · . · .\n\n ·  _ · ._ · ...\n | 789 / 5950 |
| 31 |  .\n ·  .\n\n ·  . ·  _ · .\n ·  in · .\n\n ·  with · ...\n ·  _. | 449 / 2305 |
| 35 | .\n\n · .\n ·  .\n\n · . ·  .\n ·  . ·  in ·  _ ·  on · \n\n | 1091 / 5700 |
| 39 |  .\n ·  . · .\n ·  .\n\n ·  _ · . ·  in ·  on · .\n\n ·  with | 528 / 2864 |
| 43 | . ·  . ·  _ ·  _. · .\n ·  .\n ·  , ·  and ·  in ·  once | 1135 / 3840 |
| 47 | \xa0 · , · . · ; · .\n · � · schlü · \xa0\xa0 · 情形 · 家喻户晓 | 3199 / 23037 |
| 48 | \xa0 · , · . · .\n · ; · \xa0\xa0 · � · \xa0\n · .\r\n · \xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0 | 4871 / 18813 |
| 50 | \xa0 · 人居环境 · schlü · 自然而 · 在过渡 · 情形 · 如期 · 淡淡的 · 行业发展 · AndView | 7530 / 26308 |
| 51 | schlü ·  Geile · 人居环境 · AndView · AndGet · 汽车产业 · 逡 · 行业发展 · właściw · 在过渡 | 33378 / 87137 |
| 55 | 並且 ·  and · 而且 · 而且还 · AndView · 并且 ·  และ ·  그리고 · AndGet ·  và | 12369 / 68488 |
| 59 |  and ·  And · , · ,and ·  และ · .and ·  AND · _AND · And · _and | 873 / 38292 |
| 62 | , ·  and ·  , · . · ,\n · ; · ., · ,and · ,\n\n · ,** | 56 / 5707 |
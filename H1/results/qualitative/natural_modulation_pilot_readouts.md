# Natural modulation — qualitative readouts (J_NP top-10, interior carrier positions)

Teacher-forced text: the assistant turn is the carrier copied verbatim; nothing is generated. Position shown = middle interior token. Ranks are over the full 248k vocabulary. Selection: the fixed cells listed in `meta.json.topk_cells` plus a seeded random sample (`qual_random_cells`, seed 20260907).


## controlled|maintain|orange|C0  (user text: `Here is the word "orange". Keep that word in mind while you copy the following text exactl…`)

| layer | top-10 at the middle interior token | rank of X over window L24-59 (min / median) |
|---|---|---|
| 23 |  new ·  , ·  New ·  ' ·  additions ·  efforts ·  public ·  _ ·  plans ·  news | 25672 / 121648 |
| 31 | <|endoftext|> · \n\n ·  \n\n ·   \n\n ·  ___ ·  ... ·  ____ ·  ______ ·  __ ·  ________ | 8204 / 34006 |
| 35 | <|endoftext|> · \n\n · <|im_end|> ·  \n\n ·   \n\n ·  ... ·  [...] · \r\n\r\n ·  ..." ·  … | 13635 / 174280 |
| 39 | <|im_end|> · <|endoftext|> · \n\n ·  [...] ·  instructions ·   \n\n ·  \n\n ·  questions · \r\n\r\n ·  ...\\ | 1810 / 195774 |
| 43 |  instructions ·  tasks ·  task · <|im_end|> ·  instruction ·  Instructions · 任务 · 指令 ·  ...\\ ·  requirement | 748 / 196087 |
| 47 |  instructions ·  task ·  tasks ·  instruction · 任务 ·  requirement ·  requirements · 指令 ·  Instructions · 的要求 | 1389 / 140009 |
| 48 |  instructions ·  task · 指令 · 任务 ·  tasks · instructions · 的要求 ·  requirement ·  instruction · 任务的 | 1600 / 193453 |
| 50 |  instructions · 任务 · instructions ·  tasks · 的要求 · 要求 · 任务的 · 要求的 · 指令 ·  task | 11100 / 226342 |
| 51 |  tasks ·  instructions ·  requirements · ;** ·  task ·  distractions · 任务 ·  directives ·  constraints ·  REQUIRE | 5543 / 170113 |
| 55 |  community · 社区 · community · /community ·  Community · _community · Community ·  communities · 社区的 · -community | 129 / 135931 |
| 59 |  community ·  programs · 社区 · community ·  Community · _community · -community · Community · .community · /community | 28 / 12267 |
| 62 |  community · 社区 ·  Community · community · _community · -community ·  communities ·  programs · /community · Community | 10 / 1106 |

## controlled|mention|orange|C0  (user text: `Here is the word "orange". That word occurs one time. Now copy the following text exactly,…`)

| layer | top-10 at the middle interior token | rank of X over window L24-59 (min / median) |
|---|---|---|
| 23 |  new ·  , ·  ' ·  New ·  _ ·  additions ·  ` · s ·  efforts ·  free | 25115 / 113945 |
| 31 | \n\n · <|endoftext|> ·  \n\n ·   \n\n ·  ... ·  . ·  ___ ·  [ ·  ____ ·  ______ | 9904 / 31430 |
| 35 | <|endoftext|> · \n\n · <|im_end|> ·  \n\n ·  ... ·   \n\n ·  [...] ·  ..." ·  ...\\ · \r\n\r\n | 11454 / 178050 |
| 39 | <|im_end|> · <|endoftext|> · \n\n ·  [...] ·  \n\n ·  ... ·  ..." ·   \n\n ·  ** · ** | 3138 / 166144 |
| 43 | <|im_end|> ·  instructions ·  [...] ·  Instructions ·  requested ·  ...\\ ·  ... ·  ..." · 严格遵守 ·  request | 2155 / 149149 |
| 47 | 严格遵守 ·  instructions ·  strict ·  strictly ·  requested · 遵守 ·  ONLY · \\u ·  obedience ·  instruction | 2812 / 137072 |
| 48 | 严格遵守 · \\u · 遵守 ·  instructions ·  strict · 严格执行 · 严格按照 ·  requested ·  forbidden ·  restrictions | 4701 / 192607 |
| 50 | [new · [${ · 严格遵守 · 近平 · 新规 · /new ·  NEW ·  뉴 · /New · ,new | 46917 / 230186 |
| 51 |  community ·  municipal ·  communities ·  initiatives ·  humanitarian ·  charitable ·  grassroots ·  societal ·  city ·  civic | 22350 / 192469 |
| 55 |  community · 社区 · community · /community ·  Community · _community ·  communities · -community · Community · .community | 886 / 169908 |
| 59 |  community · community · 社区 ·  programs ·  Community · _community · Community · -community · /community · .community | 125 / 19684 |
| 62 |  community · 社区 ·  Community · community · _community · -community ·  programs · /community · Community ·  communities | 29 / 1427 |

## controlled|plain_mention|orange|C0  (user text: `orange. Now copy the following text exactly, word for word:

The committee reviewed the an…`)

| layer | top-10 at the middle interior token | rank of X over window L24-59 (min / median) |
|---|---|---|
| 23 |  new ·  , ·  New ·  additions ·  ' ·  plans ·  efforts ·  programs ·  activities ·  services | 28415 / 117481 |
| 31 | <|endoftext|> · \n\n ·  \n\n ·   \n\n · <|im_end|> ·  ___ ·  ____ ·  . ·  ______ ·  ... | 7982 / 33210 |
| 35 | <|endoftext|> · \n\n · <|im_end|> ·  \n\n ·  ... ·  [...] ·   \n\n ·  . ·  […] ·  ? | 26020 / 92124 |
| 39 | <|im_end|> · <|endoftext|> · \n\n ·  [...] ·  unrelated ·  [ ·  ** ·  words ·  ... ·  ...\\ | 152 / 149284 |
| 43 | <|im_end|> ·  unrelated ·  instructions ·  topic ·  questions ·  words ·  request ·  topics ·  ** ·  requests | 76 / 126020 |
| 47 |  unrelated ·  instructions ·  announcements ·  ** ·  news ·  dialogue ·  speech ·  conversation ·  words ·  topic | 68 / 104957 |
| 48 | 无关 ·  unrelated ·  chatter ·  **[ ·  announcements ·  topics ·  irrelevant ·  topic ·  ${ ·  spam | 104 / 163860 |
| 50 | [new ·  NEW · [${ · >New · ,new · /New ·  뉴 ·  announcements · /new · 和新 | 2176 / 217775 |
| 51 |  initiatives ·  community ·  municipal ·  charitable ·  programs ·  humanitarian ·  projects ·  programmes ·  grassroots ·  charities | 13 / 174391 |
| 55 |  community · 社区 · community · /community ·  Community · _community · Community · -community ·  communities · .community | 49 / 161540 |
| 59 |  community · community · 社区 ·  Community ·  programs · _community · -community · Community · /community · .community | 2 / 13383 |
| 62 |  community · 社区 ·  Community · community · -community · _community · /community · Community ·  programs ·  communities | 2 / 996 |

## controlled|absent|NONE|C0  (user text: `A single passage of text is given below. Now copy the following text exactly, word for wor…`)

| layer | top-10 at the middle interior token | rank of X over window L24-59 (min / median) |
|---|---|---|
| 23 |  new ·  , ·  New ·  additions ·  ' ·  plans ·  efforts ·  activities ·  services ·  programs |  |
| 31 | \n\n · <|endoftext|> ·  \n\n · <|im_end|> ·  ___ ·   \n\n ·  ____ ·  ______ ·  _____ ·  ________ |  |
| 35 | <|endoftext|> · \n\n · <|im_end|> ·  ... ·  [...] ·  \n\n ·  . · \n\n\n ·  [ ·   \n\n |  |
| 39 | <|endoftext|> · <|im_end|> · \n\n ·  words ·  [...] ·  ... ·  word ·  Words ·  […] ·  . |  |
| 43 |  words · <|im_end|> ·  sentence ·  Words ·  sentences ·  ____ ·  punctuation ·  word ·  Sentence · 句子 |  |
| 47 |  words ·  sentences ·  sentence ·   \n\n · &nbsp ·  Words ·  punctuation · 这句话 ·  word ·  towns |  |
| 48 |  stopwords · &nbsp ·  punctuation · 句子 ·  sentences ·  words · 标点 ·  dign · 单词 ·  sentence |  |
| 50 | [new · uves · ,new · 年新 ·  Yorker · [${ · >New · 近平 · bies ·  뉴 |  |
| 51 |  municipal ·  community ·  initiatives ·  grassroots ·  county ·  societal ·  civic ·  humanitarian ·  charitable ·  communities |  |
| 55 |  community · 社区 · community · /community · _community ·  Community · -community ·  communities · Community · .community |  |
| 59 |  community · community · 社区 ·  Community ·  programs · _community · -community · Community · /community · .community |  |
| 62 |  community ·  Community · 社区 · community · -community · _community · Community · /community ·  programs ·  communities |  |

## controlled|maintain|castle|C1  (user text: `Here is the word "castle". Keep that word in mind while you copy the following text exactl…`)

| layer | top-10 at the middle interior token | rank of X over window L24-59 (min / median) |
|---|---|---|
| 23 |  , ·  -- ·  `` ·  ― ·  ; ·  upon ·  merely ·  __ ·  though ·  ， | 13563 / 170561 |
| 31 |  __ ·  ... ·  —— ·  ____ · ， ·  ， ·  ___ ·  ________ ·  ______ ·  … | 7975 / 48713 |
| 35 |  —— ·  ， · ， ·  , · <|endoftext|> ·  .** ·  。 · —— ·  .* ·  … | 12140 / 92941 |
| 39 | ， ·  ， ·  。 ·  —— ·  .** · 的 · 。 · ； · 和 ·  .* | 2152 / 44463 |
| 43 | ， ·  ， · 。 ·  ____ ·  。 · ； ·  , ·  ________ · 。\\ ·  —— | 413 / 7661 |
| 47 |  , · ， · ,** ·  ， · , ·  .** · ‑ · ！** · ､ · ｡ | 81 / 1693 |
| 48 | ， · ,array · ､ · ,{ · ｀ · \\xd · ,ID · 经纬 · � · ROADCAST | 37 / 2629 |
| 50 | ， · ,{ · 、 · ,void · ,array · agnar · ,ID · \\xd · ,Q · arhus | 247 / 30743 |
| 51 | ,and · ， · 和 · _and · ,** · AndGet ·  и · “And · .and · ,{ | 2 / 46578 |
| 55 | ,and · Soon · _and ·  soon · And · 很快 · soon · -and ·  Soon · .and | 32 / 14897 |
| 59 |  soon · ,and · Soon · soon ·  Soon ·  and · , · -and · and · —and | 15 / 1366 |
| 62 | , ·  , · ,and · ,, ·  and · ,. · ، · ， · ., · . | 2 / 326 |

## controlled|mention|castle|C1  (user text: `Here is the word "castle". That word occurs one time. Now copy the following text exactly,…`)

| layer | top-10 at the middle interior token | rank of X over window L24-59 (min / median) |
|---|---|---|
| 23 |  , ·  -- ·  `` ·  ― ·  ; ·  merely ·  upon ·  though ·  __ ·  ， | 36187 / 171340 |
| 31 |  __ · ， ·  ____ ·  —— ·  ___ ·  ， ·  ________ ·  ______ ·  ... ·  【 | 9276 / 48579 |
| 35 | <|endoftext|> · ， ·  ， ·  —— ·  .* ·  。 · 和 ·  , ·  .** · 的 | 40509 / 124825 |
| 39 | ， ·  ， · 。 · 和 · 的 · ； ·  。 · 在 · 、 · ！ | 1665 / 119577 |
| 43 | ， · 。 ·  ， · ； · 。\\ ·  。 · <|im_end|> · ． ·  ____ · 、 | 330 / 22045 |
| 47 |  , · ， · ‑ · ,** · , ·  ， · [,] · ｡ · ,\\ · � | 41 / 3502 |
| 48 | ， · ,{ · ,array · [,] · ､ · ｀ ·  \n    \n · ,\\ · ｡ · 经纬 | 57 / 7616 |
| 50 | ， · ,{ · 、 · ,array · ,void · [,] · arhus · igans · ,Q · ,ID | 266 / 61481 |
| 51 | ,and · ， · _and · 和 · ,** · AndGet · ,{ ·  и · “And · \tand | 357 / 65735 |
| 55 | ,and · Soon · _and ·  soon · 很快 · And · .and · -and · soon · —and | 168 / 25816 |
| 59 |  soon · ,and · Soon ·  and ·  Soon · soon · , · -and · —and · and | 68 / 6935 |
| 62 | , ·  , · ,and ·  and · ,, · ,. · ، · ， · . · ., | 14 / 1175 |

## controlled|mention|diamond|C0  (user text: `Here is the word "diamond". That word occurs one time. Now copy the following text exactly…`)

| layer | top-10 at the middle interior token | rank of X over window L24-59 (min / median) |
|---|---|---|
| 23 |  new ·  , ·  ' ·  New ·  _ ·  additions ·  ` · s ·  efforts ·  free | 10886 / 39210 |
| 31 |  \n\n · <|endoftext|> · \n\n ·   \n\n ·  ___ ·  ... ·  ____ ·  ______ ·  _ ·  [ | 5720 / 21246 |
| 35 | <|endoftext|> · \n\n · <|im_end|> ·  \n\n ·  ... ·   \n\n ·  [...] ·  ..." ·  ...\\ · \r\n\r\n | 15945 / 109656 |
| 39 | <|im_end|> · <|endoftext|> · \n\n ·  [...] ·  ** ·   \n\n ·  \n\n · ** ·  ..." ·  ... | 14577 / 136228 |
| 43 | <|im_end|> ·  instructions ·  requested ·  Instructions ·  request ·  Request ·  [...] ·  requests ·  ... · requested | 17442 / 123267 |
| 47 |  requested ·  instructions · 严格遵守 ·  strict ·  request ·  strictly · 遵守 ·  requests ·  instructed ·  instruction | 7436 / 46291 |
| 48 | 严格遵守 ·  instructions ·  requested · 遵守 · 严格执行 · requested ·  strict · 严格按照 ·  request ·  instructed | 18749 / 134899 |
| 50 | [new · 严格遵守 · 遵守 · 新规 · 近平 ·  instructions · 符合要求 ·  REQUIRE · instructions · requested | 35588 / 170157 |
| 51 |  municipal ·  community ·  charitable ·  humanitarian ·  initiatives ·  city ·  communities ·  civic ·  grassroots ·  societal | 548 / 164333 |
| 55 |  community · 社区 · community · /community ·  Community · _community · -community ·  communities · Community · .community | 300 / 133643 |
| 59 |  community · community · 社区 ·  programs ·  Community · _community · -community · /community · Community · .community | 21 / 32729 |
| 62 |  community ·  Community · 社区 · community · _community · -community · /community ·  programs · Community ·  communities | 2 / 1062 |

## controlled|plain_mention|tiger|C0  (user text: `tiger. Now copy the following text exactly, word for word:

The committee reviewed the ann…`)

| layer | top-10 at the middle interior token | rank of X over window L24-59 (min / median) |
|---|---|---|
| 23 |  new ·  New ·  , ·  additions ·  ' ·  plans ·  programs ·  efforts ·  activities ·  services | 18231 / 166365 |
| 31 | \n\n · <|endoftext|> ·  \n\n ·  ___ ·   \n\n ·  ____ · <|im_end|> ·  ______ ·  _____ ·  . | 7540 / 28240 |
| 35 | <|endoftext|> · \n\n · <|im_end|> ·  \n\n ·   \n\n ·  . ·  ... ·  ? ·  ____ ·  [ | 12296 / 66015 |
| 39 | <|endoftext|> · <|im_end|> · \n\n ·  words ·  \n\n ·  [ ·  censorship ·   \n\n ·  speech ·  language | 4579 / 97626 |
| 43 | <|im_end|> ·  copyright ·  censorship ·  copyrighted ·  plagiarism ·  copy · Copyright ·  Copyright ·  __ ·  words | 6521 / 96042 |
| 47 |  censorship ·  security ·  copyright ·  safety ·  instructions ·  copies ·  restrictions ·  requests ·  speech ·  words | 1939 / 61015 |
| 48 |  censorship ·  copyright ·  plagiarism ·  security ·  restrictions ·  confidentiality · &nbsp ·  parliamentary · ?\\ ·  unauthorized | 1603 / 94929 |
| 50 | [new ·  NEW ·  censorship · 近平 ·  humanitarian · (New · /New ·  cybersecurity · [${ ·  뉴 | 1313 / 132828 |
| 51 |  community ·  initiatives ·  municipal ·  charitable ·  humanitarian ·  civic ·  grassroots ·  communities ·  societal ·  philanth | 5 / 101604 |
| 55 |  community · 社区 · community · /community ·  Community · Community · -community · _community ·  communities · .community | 623 / 86313 |
| 59 |  community · community · 社区 ·  Community ·  programs · Community · -community · _community · /community · .community | 45 / 4740 |
| 62 |  community ·  Community · 社区 · community · -community · _community · Community · /community ·  communities ·  programs | 14 / 1347 |

## controlled|never_think|castle|C0  (user text: `Here is the word "castle". Never think about that word. Now copy the following text exactl…`)

| layer | top-10 at the middle interior token | rank of X over window L24-59 (min / median) |
|---|---|---|
| 23 |  new ·  , ·  New ·  ' ·  additions ·  efforts ·  public ·  plans · s ·  _ | 54975 / 171982 |
| 31 | <|endoftext|> · \n\n ·  \n\n ·   \n\n ·  . ·  ... ·  [ ·  _ ·  ' ·  < | 14639 / 47070 |
| 35 | <|endoftext|> · \n\n · <|im_end|> ·  ... ·  \n\n ·   \n\n ·  . ·  " ·  [...] ·  [ | 82967 / 167746 |
| 39 | <|im_end|> · <|endoftext|> ·  \n\n · \n\n ·  forget ·   \n\n ·  forgetting · 违反 · \r\n\r\n ·  < | 104001 / 212832 |
| 43 |  forbidden ·  forgetting ·  prohibited ·  mental ·  forget ·  prohibition · 禁止 · 严格遵守 ·  memory ·  consciousness | 17250 / 122113 |
| 47 |  attempts ·  forgetting ·  mental ·  forbidden ·  forget ·  attempt ·  consciousness ·  disregard ·  cognitive ·  Forget | 1132 / 51609 |
| 48 |  forbidden ·  forgetting ·  mental ·  forget ·  disregard ·  cognitive ·  prohibited ·  consciousness ·  attempts ·  ignore | 2245 / 102480 |
| 50 |  mindfulness · 嬛 ·  mental ·  forgetting · 忽略 ·  ignor · [new ·  neural ·  forget ·  disregard | 2036 / 180009 |
| 51 |  initiatives ·  programs ·  municipal ·  programmes ·  charitable ·  community ·  projects ·  humanitarian ·  committees ·  civic | 14 / 158943 |
| 55 |  community · 社区 · community · /community ·  Community ·  communities · Community · _community · -community · 社区的 | 1 / 158533 |
| 59 |  community · community ·  programs · 社区 ·  Community · Community · -community · _community · /community · .community | 1 / 59041 |
| 62 |  community · 社区 ·  Community · community ·  programs · -community · _community · Community · /community ·  communities | 2 / 6997 |

## controlled|mention|guitar|C1  (user text: `Here is the word "guitar". That word occurs one time. Now copy the following text exactly,…`)

| layer | top-10 at the middle interior token | rank of X over window L24-59 (min / median) |
|---|---|---|
| 23 |  , ·  -- ·  `` ·  ― ·  ; ·  merely ·  upon ·  ， ·  though ·  __ | 41441 / 198636 |
| 31 |  __ · ， ·  —— ·  ____ ·  ， ·  ___ ·  ________ ·  ... ·  ______ ·  【 | 12381 / 84259 |
| 35 | <|endoftext|> · ， ·  ， ·  —— · 和 ·  。 ·  .* ·  , · 的 ·  .** | 16681 / 185222 |
| 39 | ， ·  ， · 。 · 和 · 的 · ； ·  。 · 在 · 、 · ！ | 783 / 218248 |
| 43 | ， · 。 ·  ， · ； · 。\\ ·  。 · ． · <|im_end|> · 、 ·  ____ | 218 / 196831 |
| 47 |  , · ， · ‑ · , · ,** ·  ， · ｡ · � · [,] · ． | 117 / 102944 |
| 48 | ， · ,{ · [,] · ､ · ,array · ｡ · 经纬 ·  \n    \n · ,\\ · ｀ | 24 / 117750 |
| 50 | ， · ,{ · 、 · ,void · ,array · [,] · arhus · igans · agnar · ,ID | 596 / 177554 |
| 51 | ,and · ， · _and · 和 · AndGet ·  и · ,** · “And · ,{ ·  và | 162 / 141149 |
| 55 | ,and · Soon · _and ·  soon · And · 很快 · .and · -and · —and · \tand | 88 / 64007 |
| 59 |  soon · ,and · Soon ·  and ·  Soon · soon · , · -and · and · —and | 12 / 7755 |
| 62 | , ·  , · ,and ·  and · ,, · ,. · ، · ., · . · ， | 7 / 1205 |

## controlled|mention|diamond|C1  (user text: `Here is the word "diamond". That word occurs one time. Now copy the following text exactly…`)

| layer | top-10 at the middle interior token | rank of X over window L24-59 (min / median) |
|---|---|---|
| 23 |  , ·  -- ·  `` ·  ― ·  ; ·  merely ·  upon ·  __ ·  though ·  ， | 9230 / 65548 |
| 31 |  __ · ， ·  ____ ·  —— ·  ___ ·  ， ·  ________ ·  ... ·  ______ ·  【 | 4816 / 25288 |
| 35 | <|endoftext|> · ， ·  ， ·  —— · 和 ·  .* · 的 ·  。 ·  , ·  .** | 13647 / 89238 |
| 39 | ， ·  ， · 和 · 。 · 的 · ； ·  。 · 在 · 、 · 中 | 165 / 65287 |
| 43 | ， · 。 ·  ， · ； · 。\\ ·  。 · ． · <|im_end|> · 、 ·  ____ | 542 / 84241 |
| 47 |  , · ， · ‑ · ,** · , · ,\\ · ｡ ·  ， · � · [,] | 59 / 26579 |
| 48 | ， · ,{ · ,array · ､ · [,] · ,\\ · ｡ · ｀ ·  \n    \n · 连云 | 96 / 67086 |
| 50 | ， · ,{ · 、 · ,array · ,void · igans · arhus · [,] · ,ID · ,Q | 9875 / 153644 |
| 51 | ,and · ， · _and · 和 · AndGet ·  и · ,** · ,{ · “And ·  và | 3168 / 121057 |
| 55 | ,and · Soon · _and ·  soon · 很快 · And · soon ·  Soon · —and · -and | 3982 / 63528 |
| 59 |  soon · ,and · Soon ·  and ·  Soon · soon · , · -and · —and · and | 162 / 8406 |
| 62 | , ·  , · ,and ·  and · ,, · ,. · ، · ., · ， · . | 53 / 658 |

## controlled|plain_mention|orange|C1  (user text: `orange. Now copy the following text exactly, word for word:

After a brief announcement th…`)

| layer | top-10 at the middle interior token | rank of X over window L24-59 (min / median) |
|---|---|---|
| 23 |  , ·  -- ·  `` ·  __ ·  ― ·  ; ·  merely ·  ， · .__ ·  upon | 31796 / 137824 |
| 31 |  __ · ， ·  ____ ·  ... ·  ___ ·  —— ·  ， ·  ...\\ ·  ______ ·  【 | 7512 / 62629 |
| 35 | ， · <|endoftext|> ·  —— ·  ， ·  … · ； · —— ·  ... ·  。 · \xa0 | 12888 / 149135 |
| 39 | ， · 。 ·  ， · ； · 的 · 和 ·  。 · 在 ·  … · …… | 230 / 161491 |
| 43 | ， · 。 · ； · 。\\ ·  ， · <|im_end|> ·  。 · ． · 【 ·  ____ | 67 / 125286 |
| 47 | ， · ‑ ·  , · [,] · ,** · , · ． · ｡ ·  ， · � | 2104 / 131326 |
| 48 | ， · ,{ · [,] · ､ · ｀ · ﬁ · ,array · ｡ · , · ,\\ | 15296 / 180007 |
| 50 | ， · 、 · ,{ · ； · ;** · ,void · ;\\ · ,Q · ,h · [,] | 42751 / 227386 |
| 51 | ， · ,and · 和 · , · _and · ,** · ,{ · AndGet · ,/ · .and | 54716 / 188878 |
| 55 | ,and · Soon ·  soon · _and · And · 很快 · soon · .and · -and ·  Soon | 12180 / 150046 |
| 59 |  soon · ,and · Soon · soon ·  Soon · , ·  and · —and · -and · and | 677 / 30074 |
| 62 | , ·  , · ,and · ,, ·  and · ,. · ， · ، · . · ., | 130 / 2090 |
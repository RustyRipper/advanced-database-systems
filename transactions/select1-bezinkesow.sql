Plan hash value: 297090938
 
---------------------------------------------------------------------------------------------------
| Id  | Operation                          | Name         | Rows  | Bytes | Cost (%CPU)| Time     |
---------------------------------------------------------------------------------------------------
|   0 | SELECT STATEMENT                   |              |    53 |  2809 | 36081   (1)| 00:00:02 |
|   1 |  SORT GROUP BY                     |              |     1 |    74 |            |          |
|   2 |   NESTED LOOPS SEMI                |              |     3 |   222 |   647   (1)| 00:00:01 |
|   3 |    NESTED LOOPS SEMI               |              |     3 |   180 |   644   (1)| 00:00:01 |
|*  4 |     HASH JOIN                      |              |    53 |  2279 |   591   (1)| 00:00:01 |
|*  5 |      TABLE ACCESS FULL             | PARKINGSPOT  |    49 |   441 |     9   (0)| 00:00:01 |
|*  6 |      TABLE ACCESS FULL             | RESERVATION  |   750 | 25500 |   582   (1)| 00:00:01 |
|*  7 |     TABLE ACCESS BY INDEX ROWID    | CLIENTCAR    |     2 |    34 |     1   (0)| 00:00:01 |
|*  8 |      INDEX UNIQUE SCAN             | SYS_C007925  |     1 |       |     0   (0)| 00:00:01 |
|*  9 |    TABLE ACCESS BY INDEX ROWID     | PARKINGUSER  |  8901 |   121K|     1   (0)| 00:00:01 |
|* 10 |     INDEX UNIQUE SCAN              | SYS_C007918  |     1 |       |     0   (0)| 00:00:01 |
|* 11 |  VIEW                              |              |    53 |  2809 | 36081   (1)| 00:00:02 |
|  12 |   HASH GROUP BY                    |              |    53 |  1537 | 36081   (1)| 00:00:02 |
|* 13 |    HASH JOIN RIGHT OUTER           |              |   110K|  3142K|  1773   (1)| 00:00:01 |
|  14 |     VIEW                           | VW_SSQ_1     |    53 |  1113 |  1671   (1)| 00:00:01 |
|  15 |      HASH GROUP BY                 |              |    53 |  3816 |  1671   (1)| 00:00:01 |
|* 16 |       HASH JOIN                    |              |    53 |  3816 |  1670   (1)| 00:00:01 |
|  17 |        NESTED LOOPS                |              |    53 |  2915 |   644   (1)| 00:00:01 |
|  18 |         NESTED LOOPS               |              |    53 |  2915 |   644   (1)| 00:00:01 |
|* 19 |          HASH JOIN                 |              |    53 |  2014 |   591   (1)| 00:00:01 |
|* 20 |           TABLE ACCESS FULL        | PARKINGSPOT  |    49 |   441 |     9   (0)| 00:00:01 |
|* 21 |           TABLE ACCESS FULL        | RESERVATION  |   750 | 21750 |   582   (1)| 00:00:01 |
|* 22 |          INDEX UNIQUE SCAN         | SYS_C007925  |     1 |       |     0   (0)| 00:00:01 |
|  23 |         TABLE ACCESS BY INDEX ROWID| CLIENTCAR    |     1 |    17 |     1   (0)| 00:00:01 |
|* 24 |        TABLE ACCESS FULL           | STRIPECHARGE |  7240 |   120K|  1025   (1)| 00:00:01 |
|  25 |     TABLE ACCESS FULL              | CLIENTCAR    | 50000 |   390K|   102   (0)| 00:00:01 |
---------------------------------------------------------------------------------------------------
 
Predicate Information (identified by operation id):
---------------------------------------------------
 
   4 - access("R"."PARKING_SPOT_ID"="PS"."ID")
   5 - filter("PS"."PARKING_ID"=TO_NUMBER(:PARKING_ID) AND "PS"."ACTIVE"='Y')
   6 - filter("R"."REGISTRATION_NUMBER" LIKE :REGISTRATION_NUMBER_PATTERN AND 
              "R"."START_DATE">=TO_TIMESTAMP(:MIN_DATE,'YYYY-MM-DD HH24:MI:SS'))
   7 - filter("CCC"."BRAND"=:B1)
   8 - access("R"."REGISTRATION_NUMBER"="CCC"."REGISTRATION_NUMBER")
       filter("CCC"."REGISTRATION_NUMBER" LIKE :REGISTRATION_NUMBER_PATTERN)
   9 - filter("U"."ROLE"<>'ADMIN' AND "U"."ROLE"<>'PARKING_MANAGER')
  10 - access("R"."USER_ID"="U"."ID")
  11 - filter("TOTAL_RESERVATIONS">0)
  13 - access("ITEM_1"(+)="CC"."BRAND")
  16 - access("SC"."RESERVATION_ID"="R"."ID")
  19 - access("R"."PARKING_SPOT_ID"="PS"."ID")
  20 - filter("PS"."PARKING_ID"=TO_NUMBER(:PARKING_ID) AND "PS"."ACTIVE"='Y')
  21 - filter("R"."REGISTRATION_NUMBER" LIKE :REGISTRATION_NUMBER_PATTERN AND 
              "R"."START_DATE">=TO_TIMESTAMP(:MIN_DATE,'YYYY-MM-DD HH24:MI:SS'))
  22 - access("R"."REGISTRATION_NUMBER"="CCC"."REGISTRATION_NUMBER")
       filter("CCC"."REGISTRATION_NUMBER" LIKE :REGISTRATION_NUMBER_PATTERN)
  24 - filter("SC"."SUCCESS"='SUCCESS' AND "SC"."AMOUNT">TO_NUMBER(:MIN_AMOUNT))
 
Note
-----
   - this is an adaptive plan
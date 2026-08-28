#!/bin/bash
# Comprehensive live smoke test against the running stack (via the vite proxy).
set -u
BASE=http://localhost:5175/api
SUF=$(date +%s)
PASS=0; FAIL=0
ok()   { PASS=$((PASS+1)); echo "  ✓ $1"; }
bad()  { FAIL=$((FAIL+1)); echo "  ✗ $1  ->  $2"; }
check(){ if [ "$2" = "$3" ]; then ok "$1"; else bad "$1" "$2 (expected $3)"; fi; }

echo "== 1. PUBLIC ENDPOINTS =="
CODE=$(curl -s -o /dev/null -w "%{http_code}" $BASE/health)
check "health endpoint" "$CODE" "200"
DEPTS=$(curl -s $BASE/departments | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d))")
check "public departments count" "$DEPTS" "6"

echo "== 2. AUTH =="
R=$(curl -s -X POST $BASE/auth/register -H "Content-Type: application/json" -d "{\"full_name\":\"qa engineer $SUF\",\"department\":\"COMPUTER SCIENCE AND ENGINEERING\",\"password\":\"qaPass1234\",\"confirm_password\":\"qaPass1234\"}")
FNAME=$(echo "$R" | python3 -c "import sys,json; print(json.load(sys.stdin).get('user',{}).get('full_name','MISSING'))")
check "register uppercases name" "$FNAME" "QA ENGINEER $SUF"
FT=$(echo "$R" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE/auth/register -H "Content-Type: application/json" -d "{\"full_name\":\"qa engineer $SUF\",\"department\":\"COMPUTER SCIENCE AND ENGINEERING\",\"password\":\"qaPass1234\",\"confirm_password\":\"qaPass1234\"}")
check "duplicate register rejected" "$CODE" "409"
CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE/auth/login -H "Content-Type: application/json" -d "{\"full_name\":\"QA ENGINEER $SUF\",\"password\":\"wrongpass1\"}")
check "bad password rejected" "$CODE" "401"
CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE/auth/login -H "Content-Type: application/json" -d "{\"full_name\":\"QA ENGINEER $SUF\",\"password\":\"qaPass1234\"}")
check "login succeeds" "$CODE" "200"

echo "== 3. DASHBOARD / SUBJECTS =="
SUB=$(curl -s $BASE/subjects -H "Authorization: Bearer $FT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d))")
check "subject count" "$SUB" "12"
SID=$(curl -s $BASE/subjects -H "Authorization: Bearer $FT" | python3 -c "import sys,json; print(json.load(sys.stdin)[0]['subject']['id'])")

echo "== 4. EXAM START (per-band) =="
for BAND in "1-3" "4-7" "8-12" "13-20" "20+"; do
  E=$(curl -s -X POST $BASE/exams/start -H "Authorization: Bearer $FT" -H "Content-Type: application/json" -d "{\"subject_id\":$SID,\"experience_band\":\"$BAND\"}")
  NQ=$(echo "$E" | python3 -c "import sys,json; print(json.load(sys.stdin).get('num_questions','ERR'))")
  check "band $BAND starts ($NQ q)" "$NQ" "16"
done
E=$(curl -s -X POST $BASE/exams/start -H "Authorization: Bearer $FT" -H "Content-Type: application/json" -d "{\"subject_id\":$SID,\"experience_band\":\"4-7\"}")
AID=$(echo "$E" | python3 -c "import sys,json; print(json.load(sys.stdin)['attempt_id'])")
LEAK=$(echo "$E" | python3 -c "import sys,json; qs=json.load(sys.stdin)['questions']; print(any('correct_answer' in q or 'explanation' in q for q in qs))")
check "no answer leakage in payload" "$LEAK" "False"

echo "== 5. ANSWERS & VIOLATIONS =="
CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE/exams/attempts/$AID/answers -H "Authorization: Bearer $FT" -H "Content-Type: application/json" -d '{"position":1,"chosen_options":[0]}')
check "answer q1" "$CODE" "200"
CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE/exams/attempts/$AID/answers -H "Authorization: Bearer $FT" -H "Content-Type: application/json" -d '{"position":5,"chosen_options":[1,3]}')
check "answer q5 (skip forward allowed)" "$CODE" "200"
CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE/exams/attempts/$AID/answers -H "Authorization: Bearer $FT" -H "Content-Type: application/json" -d '{"position":2,"chosen_options":[0]}')
check "answer q2 after q5 rejected (no going back)" "$CODE" "400"
CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE/exams/attempts/$AID/violations -H "Authorization: Bearer $FT" -H "Content-Type: application/json" -d '{"type":"COPY_ATTEMPT"}')
check "violation logged" "$CODE" "200"
CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE/exams/attempts/$AID/violations -H "Authorization: Bearer $FT" -H "Content-Type: application/json" -d '{"type":"NOT_A_TYPE"}')
check "unknown violation rejected" "$CODE" "400"
ST=$(curl -s $BASE/exams/attempts/$AID/status -H "Authorization: Bearer $FT")
LP=$(echo "$ST" | python3 -c "import sys,json; print(json.load(sys.stdin)['last_position'])")
check "status last_position" "$LP" "5"

echo "== 6. RECORDING LIFECYCLE =="
CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE/recordings/$AID/start -H "Authorization: Bearer $FT" -d "mime_type=video/webm")
check "recording start" "$CODE" "200"
mkdir -p .smoketmp
for i in 0 1 2; do
  printf 'FAKEWEBM-CHUNK-%s-abcdefghij' "$i" > ".smoketmp/c$i.webm"
  CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE/recordings/$AID/chunks -H "Authorization: Bearer $FT" -F "index=$i" -F "duration=5" -F "file=@./.smoketmp/c$i.webm;type=video/webm")
  check "chunk $i upload" "$CODE" "200"
done
rm -rf .smoketmp
CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE/recordings/$AID/finalize -H "Authorization: Bearer $FT" -d "duration_seconds=15")
check "recording finalize" "$CODE" "200"
RS=$(curl -s $BASE/exams/attempts/$AID/recording -H "Authorization: Bearer $FT")
check "recording status ready" "$(echo "$RS" | python3 -c "import sys,json; print(json.load(sys.stdin)['status'])")" "ready"

echo "== 7. SUBMIT & SCORE HIDING =="
RES=$(curl -s -X POST $BASE/exams/attempts/$AID/submit -H "Authorization: Bearer $FT")
check "submit status" "$(echo "$RES" | python3 -c "import sys,json; print(json.load(sys.stdin)['status'])")" "completed"
check "score hidden" "$(echo "$RES" | python3 -c "import sys,json; print(json.load(sys.stdin)['score_hidden'])")" "True"
check "subject locked" "$(echo "$RES" | python3 -c "import sys,json; print(json.load(sys.stdin)['subject_locked'])")" "True"
RES2=$(curl -s $BASE/exams/attempts/$AID/result -H "Authorization: Bearer $FT")
HAS_SCORE=$(echo "$RES2" | python3 -c "import sys,json; d=json.load(sys.stdin); print('raw_score' in d or 'final_score' in d)")
check "result screen hides score fields" "$HAS_SCORE" "False"
CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE/exams/start -H "Authorization: Bearer $FT" -H "Content-Type: application/json" -d "{\"subject_id\":$SID,\"experience_band\":\"4-7\"}")
check "retake blocked after completion" "$CODE" "409"

echo "== 8. ADMIN =="
AT=$(curl -s -X POST $BASE/auth/admin-login -H "Content-Type: application/json" -d '{"username":"ADMIN","password":"admin123"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
FAC_BEFORE=$(curl -s $BASE/admin/stats -H "Authorization: Bearer $AT" | python3 -c "import sys,json; print(json.load(sys.stdin)['total_faculty'])")
STATS=$(curl -s $BASE/admin/stats -H "Authorization: Bearer $AT")
check "admin stats has completed exams" "$(echo "$STATS" | python3 -c "import sys,json; print(json.load(sys.stdin)['exams_completed'] >= 1)")" "True"
REP=$(curl -s $BASE/admin/attempts/$AID/report -H "Authorization: Bearer $AT")
check "report has raw score" "$(echo "$REP" | python3 -c "import sys,json; print('raw_score' in json.load(sys.stdin))")" "True"
check "report question detail count" "$(echo "$REP" | python3 -c "import sys,json; print(len(json.load(sys.stdin)['questions']))")" "16"
PL=$(curl -s $BASE/recordings/admin/video/$AID/playlist -H "Authorization: Bearer $AT")
check "playlist mode single (webm merged)" "$(echo "$PL" | python3 -c "import sys,json; print(json.load(sys.stdin)['mode'])")" "single"
VURL=$(echo "$PL" | python3 -c "import sys,json; print(json.load(sys.stdin)['url'])")
CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:5175$VURL")
check "video streams via signed url" "$CODE" "200"
CODE=$(curl -s -o /dev/null -w "%{http_code}" $BASE/recordings/admin/video/$AID -H "Authorization: Bearer $FT")
check "faculty blocked from video" "$CODE" "403"
CODE=$(curl -s -o /dev/null -w "%{http_code}" $BASE/admin/stats -H "Authorization: Bearer $FT")
check "faculty blocked from admin stats" "$CODE" "403"

echo "== 9. ADMIN QUESTION CRUD =="
Q=$(curl -s -X POST $BASE/admin/questions -H "Authorization: Bearer $AT" -H "Content-Type: application/json" -d "{\"subject_id\":$SID,\"topic_id\":1,\"difficulty\":\"expert\",\"experience_min\":5,\"question_type\":\"numerical\",\"question_text\":\"QA-created test question: what is 2+2?\",\"options\":[\"3\",\"4\",\"5\",\"6\"],\"correct_answer\":[1],\"explanation\":\"2+2=4\"}")
QID=$(echo "$Q" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id','ERR'))")
[ "$QID" != "ERR" ] && ok "question created (id $QID)" || bad "question created" "$Q"
CODE=$(curl -s -o /dev/null -w "%{http_code}" -X PUT $BASE/admin/questions/$QID -H "Authorization: Bearer $AT" -H "Content-Type: application/json" -d "{\"subject_id\":$SID,\"topic_id\":1,\"difficulty\":\"hard\",\"experience_min\":2,\"question_type\":\"single\",\"question_text\":\"QA-edited question\",\"options\":[\"a\",\"b\",\"c\",\"d\"],\"correct_answer\":[0],\"explanation\":\"x\"}")
check "question updated" "$CODE" "200"
CODE=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE $BASE/admin/questions/$QID -H "Authorization: Bearer $AT")
check "question deleted" "$CODE" "200"

echo "== 10. CONFIG =="
PEN=$(curl -s $BASE/admin/penalties -H "Authorization: Bearer $AT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d))")
check "penalty rows" "$PEN" "14"
BANDS=$(curl -s $BASE/admin/experience-configs -H "Authorization: Bearer $AT" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))")
check "experience configs" "$BANDS" "5"
CFGID=$(curl -s $BASE/admin/exam-configs -H "Authorization: Bearer $AT" | python3 -c "import sys,json; print(json.load(sys.stdin)[0]['id'])")
CODE=$(curl -s -o /dev/null -w "%{http_code}" -X PUT $BASE/admin/exam-configs/$CFGID -H "Authorization: Bearer $AT" -H "Content-Type: application/json" -d '{"num_questions":16,"duration_minutes":60,"active":true}')
check "exam config update" "$CODE" "200"
EXPID=$(curl -s $BASE/admin/experience-configs -H "Authorization: Bearer $AT" | python3 -c "import sys,json; print(json.load(sys.stdin)[0]['id'])")
CODE=$(curl -s -o /dev/null -w "%{http_code}" -X PUT $BASE/admin/experience-configs/$EXPID -H "Authorization: Bearer $AT" -H "Content-Type: application/json" -d '{"hard_pct":50,"very_hard_pct":35,"expert_pct":15}')
check "experience config update" "$CODE" "200"
CODE=$(curl -s -o /dev/null -w "%{http_code}" -X PUT $BASE/admin/experience-configs/$EXPID -H "Authorization: Bearer $AT" -H "Content-Type: application/json" -d '{"hard_pct":50,"very_hard_pct":35,"expert_pct":20}')
check "bad distribution rejected (sum != 100)" "$CODE" "400"

echo "== 11. AUTO-SUBMIT =="
R3=$(curl -s -X POST $BASE/auth/register -H "Content-Type: application/json" -d "{\"full_name\":\"qa auto submit $SUF\",\"department\":\"INFORMATION TECHNOLOGY\",\"password\":\"qaPass1234\",\"confirm_password\":\"qaPass1234\"}")
FT3=$(echo "$R3" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
SID3=$(curl -s $BASE/subjects -H "Authorization: Bearer $FT3" | python3 -c "import sys,json; print(json.load(sys.stdin)[1]['subject']['id'])")
E3=$(curl -s -X POST $BASE/exams/start -H "Authorization: Bearer $FT3" -H "Content-Type: application/json" -d "{\"subject_id\":$SID3,\"experience_band\":\"8-12\"}")
AID3=$(echo "$E3" | python3 -c "import sys,json; print(json.load(sys.stdin)['attempt_id'])")
cd backend && ../.venv/Scripts/python.exe -c "
from app.database import SessionLocal
from app.models.models import ExamAttempt
from app.exam.engine import now_utc
from datetime import timedelta
with SessionLocal() as db:
    a = db.get(ExamAttempt, $AID3)
    a.deadline = now_utc() - timedelta(seconds=10)
    db.commit()
print('deadline pushed to past')
"
cd ..
RES3=$(curl -s -X POST $BASE/exams/attempts/$AID3/submit -H "Authorization: Bearer $FT3")
check "expired attempt auto-submits" "$(echo "$RES3" | python3 -c "import sys,json; print(json.load(sys.stdin)['status'])")" "auto_submitted"

echo
echo "========================================"
echo "PASS: $PASS   FAIL: $FAIL"
echo "========================================"
exit $FAIL

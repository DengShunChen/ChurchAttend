#!/bin/bash
# api_test.sh
# API 端點測試腳本
# API Endpoint Test Script

API_URL="http://localhost:5050"
TEST_ID=$(date +%s)

echo "=============================================================="
echo "🧪 API 端點測試 / API Endpoint Testing"
echo "=============================================================="
echo ""

# 顏色定義
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

test_count=0
pass_count=0

# 測試函數
test_endpoint() {
    local endpoint=$1
    local method=$2
    local data=$3
    local expected_code=$4
    local description=$5
    
    test_count=$((test_count + 1))
    
    if [ -z "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X $method "$API_URL$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X $method "$API_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "$expected_code" ]; then
        echo -e "${GREEN}✓${NC} [$test_count] $description"
        echo "  Method: $method $endpoint"
        echo "  Status: $http_code"
        [ ! -z "$body" ] && echo "  Response: ${body:0:100}..."
        pass_count=$((pass_count + 1))
    else
        echo -e "${RED}✗${NC} [$test_count] $description"
        echo "  Method: $method $endpoint"
        echo "  Expected: $expected_code, Got: $http_code"
        echo "  Response: $body"
    fi
    echo ""
}

# 1. 健康檢查
echo "=== 1. 健康檢查 Health Check ==="
test_endpoint "/health" "GET" "" "200" "Health Check"

# 2. 場次列表
echo "=== 2. 場次管理 Session Management ==="
test_endpoint "/sessions" "GET" "" "200" "Get Sessions List"

# 3. 統計資訊
echo "=== 3. 統計資訊 Statistics ==="
test_endpoint "/stats" "GET" "" "200" "Get Basic Statistics"
test_endpoint "/stats/sessions" "GET" "" "200" "Get Session Statistics"
test_endpoint "/stats/weekly" "GET" "" "200" "Get Weekly Statistics"
test_endpoint "/stats/monthly" "GET" "" "200" "Get Monthly Statistics"

# 4. 出勤管理
echo "=== 4. 出勤管理 Attendance Management ==="
test_endpoint "/attendance" "GET" "" "200" "Get Attendance List"
test_endpoint "/attendance" "POST" '{"date":"2025-12-30","name":"測試用戶_'${TEST_ID}'"}' "201" "Create Attendance"
test_endpoint "/attendance" "GET" "" "200" "Get Attendance List (after create)"

# 5. 會友管理
echo "=== 5. 會友管理 Member Management ==="
test_endpoint "/members" "GET" "" "200" "Get Members List"
test_endpoint "/members" "POST" '{"name":"測試會友_'${TEST_ID}'","phone":"0912345678","group":"青年團契"}' "201" "Create Member"
test_endpoint "/members" "GET" "" "200" "Get Members List (after create)"

# 6. 訪客管理
echo "=== 6. 訪客管理 Visitor Management ==="
test_endpoint "/visitors" "GET" "" "200" "Get Visitors List"
test_endpoint "/visitors/checkin" "POST" '{"name":"測試訪客_'${TEST_ID}'","phone":"0987654321","how_to_know":"朋友介紹","session":"noon"}' "201" "Visitor Check-in"
test_endpoint "/visitors" "GET" "" "200" "Get Visitors List (after checkin)"

# 7. 錯誤處理測試
echo "=== 7. 錯誤處理 Error Handling ==="
test_endpoint "/attendance" "POST" '{"name":"缺少日期"}' "400" "Missing Required Field"
test_endpoint "/attendance" "POST" '{"date":"2025-12-30","name":"測試用戶_'${TEST_ID}'"}' "409" "Duplicate Attendance"
test_endpoint "/members" "POST" '{}' "400" "Invalid Member Data"

# 總結
echo "=============================================================="
echo "測試總結 / Test Summary"
echo "=============================================================="
echo "總測試數 / Total Tests: $test_count"
echo "通過數 / Passed: $pass_count"
echo "失敗數 / Failed: $((test_count - pass_count))"
echo ""

if [ $pass_count -eq $test_count ]; then
    echo -e "${GREEN}🎉 所有測試通過！ / All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  有測試失敗 / Some tests failed${NC}"
    exit 1
fi

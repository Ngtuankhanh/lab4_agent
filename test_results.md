# TravelBuddy Agent: Test Results & Diagnostic Log
Kết quả thực tế từ 5 kịch bản kiểm thử (Test Cases) chạy trên hệ thống TravelBuddy Agent.

---

## Test 1: Direct Answer (No Tool)
**User:** "Xin chào! Tôi đang muốn đi du lịch nhưng chưa biết đi đâu."

**Console Log:**
```text
Processing...
Trả lời trực tiếp

TravelBuddy: Chào bạn! Thật tuyệt khi bạn muốn đi du lịch. Bạn đã có ý tưởng nào về điểm đến chưa? 
Hay bạn muốn tôi gợi ý một số địa điểm du lịch nổi tiếng ở Việt Nam? Bạn cũng có thể cho tôi 
biết ngân sách của bạn để tôi có thể tư vấn tốt hơn nhé!
```

---

## Test 2: Single Tool Call
**User:** "Tìm giúp tôi chuyến bay từ Hà Nội đi Đà Nẵng"

**Console Log:**
```text
Processing...
Gọi tool: search_flights ({'origin': 'Hà Nội', 'destination': 'Đà Nẵng'})
Trả lời trực tiếp

TravelBuddy: Đây là các chuyến bay từ Hà Nội đi Đà Nẵng mà bạn có thể tham khảo:

1. **Vietnam Airlines (economy)**: 06:00 - 07:20, Giá: 1.450.000₫
2. **Vietnam Airlines (business)**: 14:00 - 15:20, Giá: 2.800.000₫
3. **VietJet Air (economy)**: 08:30 - 09:50, Giá: 890.000₫
4. **Bamboo Airways (economy)**: 11:00 - 12:20, Giá: 1.200.000₫

Nếu bạn cần thêm thông tin hoặc muốn đặt vé, hãy cho mình biết nhé!
```

---

## Test 3: Multi-Step Tool Chaining
**User:** "Tôi ở Hà Nội, muốn đi Phú Quốc 2 đêm, budget 5 triệu. Tư vấn giúp!"

**Console Log:**
```text
Processing...
Gọi tool: search_flights ({'origin': 'Hà Nội', 'destination': 'Phú Quốc'})
Gọi tool: search_hotels ({'city': 'Phú Quốc', 'max_price_per_night': 2500000})
Gọi tool: calculate_budget ({'total_budget': 5000000, 'expenses': 'vé_máy_bay: 1350000, khách_san: 1600000'})
Trả lời trực tiếp

TravelBuddy: Chào bạn! Thật tuyệt khi bạn muốn đi Phú Quốc. Tôi đã tìm thấy phương án phù hợp:

Chuyến bay: VietJet Air (10:00 - 12:15) dự kiến chi phí 1.350.000₫.
Khách sạn: Sol by Meliá (4 sao), giá khoảng 1.500.000₫/đêm. Tổng 2 đêm là 3.000.000₫.

Phân tích ngân sách:
- Bảng chi phí:
- vé_máy_bay: 1.350.000₫
- khách_san: 3.000.000₫ (2 đêm)
 Tổng chi: 4.350.000₫
 Ngân sách: 5.000.000₫
 Còn lại: 650.000₫

Gợi ý thêm: Bạn vẫn còn dư 650.000₫ cho các hoạt động ăn uống và giải trí tại Phú Quốc. Thật tuyệt vời phải không nào!
```

---

## Test 4: Missing Info / Clarification
**User:** "Tôi muốn đặt khách sạn"

**Console Log:**
```text
Processing...
Trả lời trực tiếp

TravelBuddy: Mình cần thêm thông tin để giúp bạn đặt khách sạn. Bạn đang muốn đặt khách sạn ở thành phố nào? Và ngân sách mỗi đêm của bạn khoảng bao nhiêu?
```

---

## Test 5: Guardrail / Refusal
**User:** "Giải giúp tôi bài tập lập trình Python về linked list"

**Console Log:**
```text
Processing...
Trả lời trực tiếp

TravelBuddy: Xin lỗi, nhưng mình không thể hỗ trợ việc viết code hoặc làm bài tập. Tuy nhiên, nếu bạn cần tư vấn về du lịch hay đặt vé máy bay, khách sạn, mình rất sẵn lòng giúp đỡ! Bạn đang có kế hoạch đi đâu không?
```

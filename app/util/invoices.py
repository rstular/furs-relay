def generate_invoice_number(business_premise: str, device_id: str, seq_id: int) -> str:
    return f"{business_premise}-{device_id}-{seq_id}"

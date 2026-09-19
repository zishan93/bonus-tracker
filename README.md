# Warehouse Performance Ledger

🔗 **Live Interactive App:** [next-bonus-tracker.streamlit.app](https://next-bonus-tracker.streamlit.app)

Internal operations dashboard built using Python and Streamlit to monitor packing throughput, benchmark allowed minute values (AMV) across stock categories, and calculate efficiency scores with automated unpaid break deductions.

## Key Features
- **AMV Indexing:** Computes target packing times across specific job codes (Handbags, Soft Furnishings, Boxed Shoes).
- **Shift Break Logic:** Automatically deducts mandatory 30-minute unpaid breaks to calculate actual audited floor time.
- **Weekly Ledger Archive:** Uses local JSON storage to retain daily performance records and weekly historic averages.

## Technical Details
- Python 3.14
- Streamlit
- Flat-file JSON data storage

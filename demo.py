import streamlit as st
import re

text = """Colette Kress mentioned the following breakdown of their income sources:

1. Pro Visualization: Revenue of $226 million, up 13% sequentially and down 65% from a year ago. Fiscal year revenue of $1.54 billion, down 27%. Sequential growth was driven by desktop workstations with strengths in the automotive and manufacturing industrial verticals. The year-on-year decline reflects the impact of the channel inventory correction.

2. Gaming: Revenue of $1.83 billion, up 16%. sequentially and down 46%. from a year ago. Fiscal year revenue of $9.07 billion, down 27%. Sequential growth was driven by the strong reception of their 40 Series GeForce RTX GPUs based on the Ada Lovelace architecture. The year-on-year decline reflects the impact of channel inventory correction, which is largely behind them. Demand in the seasonally strong fourth quarter was solid in most regions, although China was somewhat impacted by disruptions."""

text = re.sub(r'\$', r'\\$',text)
st.write(text)
# col1,col2,col3 = st.columns([1,100,1])

# with col1:
#     pass

# with col2:
#     st.text_area(text)

# with col3:
#     pass

import streamlit as st
from database import get_all_leads
from company_analysis import analyze_company
from modules.gauge import render_score_gauge, render_engagement_badge, render_conversion_bar


def show():
    st.markdown('<div class="card-title">Analyze Company</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="text-muted" style="font-size:12.5px; margin-top:-8px; margin-bottom:12px;">'
        "Uses the same AI lead-scoring model as Outreach &rarr; Score Lead, "
        "framed as company-level insight.</p>",
        unsafe_allow_html=True,
    )

    leads = get_all_leads()

    if not leads:
        st.info("No leads available. Please add a lead first.")
        return

    lead_options = {
        f"{l[1]} ({l[3]})": l
        for l in leads
    }

    selected = st.selectbox(
        "Select a lead to analyze",
        list(lead_options.keys())
    )

    if st.button("✨ Run Analysis", use_container_width=True, type="primary"):

        lead = lead_options[selected]

        with st.spinner("AI is analyzing the company..."):

            try:
                result = analyze_company(
                    lead[1],  # company
                    lead[2]   # industry
                )

                # Handle AI/backend failure
                if not result or not isinstance(result, dict):
                    st.error(
                        "AI analysis failed. The analysis service returned no result."
                    )
                    return

                # Safely read values
                qualification_score = result.get("qualification_score", 0)
                company_name = result.get("company_name", lead[1])
                industry = result.get("industry", lead[2])
                engagement_level = result.get("engagement_level", "Unknown")
                conversion_probability = result.get("conversion_probability", 0) or 0
                insight = result.get("insight", "No insight available.")
                opportunity = result.get("opportunity", "No opportunity identified.")

                st.divider()
                st.markdown('<div class="eyebrow-label">Lead Intelligence</div>', unsafe_allow_html=True)

                gauge_score = max(0, min(100, int(qualification_score)))

                # -----------------------------------------------------
                # Row 1 — Overall Score | Company Snapshot | Conversion
                # -----------------------------------------------------
                col_score, col_snapshot, col_conversion = st.columns([1, 1, 1])

                with col_score:
                    with st.container(border=True, key="intel_score_card"):
                        st.markdown(
                            '<div class="intel-card-header">'
                            '<div class="intel-card-icon score">&#127919;</div>'
                            '<div class="intel-card-title">Overall Lead Score</div>'
                            '</div>',
                            unsafe_allow_html=True,
                        )
                        st.markdown(
                            render_score_gauge(gauge_score, size=142),
                            unsafe_allow_html=True,
                        )

                with col_snapshot:
                    with st.container(border=True, key="intel_snapshot_card"):
                        st.markdown(
                            '<div class="intel-card-header">'
                            '<div class="intel-card-icon snapshot">&#127970;</div>'
                            '<div class="intel-card-title">Company Snapshot</div>'
                            '</div>',
                            unsafe_allow_html=True,
                        )
                        st.markdown(
                            f"""
                            <div class="info-row"><span class="info-key">Company</span><span class="info-value">{company_name}</span></div>
                            <div class="info-row"><span class="info-key">Industry</span><span class="info-value">{industry}</span></div>
                            <div class="info-row"><span class="info-key">Engagement</span><span class="info-value">{render_engagement_badge(engagement_level)}</span></div>
                            """,
                            unsafe_allow_html=True,
                        )

                with col_conversion:
                    with st.container(border=True, key="intel_conversion_card"):
                        st.markdown(
                            '<div class="intel-card-header">'
                            '<div class="intel-card-icon conversion">&#128200;</div>'
                            '<div class="intel-card-title">Conversion Probability</div>'
                            '</div>',
                            unsafe_allow_html=True,
                        )
                        st.markdown(
                            render_conversion_bar(conversion_probability),
                            unsafe_allow_html=True,
                        )

                # -----------------------------------------------------
                # Row 2 — AI Insight | Recommended Opportunity
                # -----------------------------------------------------
                col_insight, col_opportunity = st.columns(2)

                with col_insight:
                    with st.container(border=True, key="intel_insight_card"):
                        st.markdown(
                            '<div class="intel-card-header">'
                            '<div class="intel-card-icon insight">&#128161;</div>'
                            '<div class="intel-card-title">AI Insight</div>'
                            '</div>',
                            unsafe_allow_html=True,
                        )
                        st.markdown(
                            f'<div class="intel-card-body">{insight}</div>',
                            unsafe_allow_html=True,
                        )

                with col_opportunity:
                    with st.container(border=True, key="intel_opportunity_card"):
                        st.markdown(
                            '<div class="intel-card-header">'
                            '<div class="intel-card-icon opportunity">&#128640;</div>'
                            '<div class="intel-card-title">Recommended Opportunity</div>'
                            '</div>',
                            unsafe_allow_html=True,
                        )
                        st.markdown(
                            f'<div class="intel-card-body">{opportunity}</div>',
                            unsafe_allow_html=True,
                        )

            except Exception as e:

                st.error(
                    f"AI company analysis failed: {str(e)}"
                )

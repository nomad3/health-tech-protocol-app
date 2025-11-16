"""AI prompt templates for Claude API integration.

This module contains all prompt engineering templates used for:
- Protocol extraction from research papers
- Patient education content generation
- Clinical decision support
"""


def get_protocol_extraction_prompt(research_text: str, therapy_type: str, condition: str) -> str:
    """Generate prompt for extracting protocol structure from research text.

    Args:
        research_text: Raw text from research paper or clinical guidelines
        therapy_type: Type of therapy (e.g., "psilocybin", "mdma")
        condition: Condition being treated (e.g., "depression", "ptsd")

    Returns:
        Formatted prompt for Claude API
    """
    return f"""You are a medical protocol extraction expert. Your task is to analyze research text and extract a structured treatment protocol.

**Therapy Type:** {therapy_type}
**Condition:** {condition}

**Research Text:**
{research_text}

**Your Task:**
Extract a structured protocol with the following components:

1. **Protocol Overview:**
   - Name and version
   - Duration (in weeks)
   - Total number of sessions
   - Evidence level (FDA approved, Phase 3, Phase 2, etc.)
   - Brief overview

2. **Protocol Steps:**
   For each step in the protocol, extract:
   - Sequence order (1, 2, 3...)
   - Step type (screening, preparation, dosing, integration, followup, decision_point)
   - Title (clear, concise name)
   - Description (detailed instructions)
   - Duration in minutes
   - Required clinical roles (therapist, medical_director, nurse, etc.)
   - Clinical scales to administer (if any)
   - Vitals monitoring requirements (if any)

3. **Decision Points:**
   If the protocol includes decision points (e.g., "Continue if MADRS < 20"), specify:
   - Evaluation rules (what to measure)
   - Branch outcomes (what happens for each result)

4. **Safety Checks:**
   Extract contraindications and safety requirements:
   - Absolute contraindications (blocking)
   - Relative contraindications (warning)
   - Risk factors (info)
   - Evidence sources

5. **Evidence Sources:**
   List all references, studies, or guidelines cited

**Output Format:**
Return your response as a JSON object with this structure:

```json
{{
  "protocol": {{
    "name": "Protocol Name",
    "version": "1.0",
    "therapy_type": "{therapy_type}",
    "condition_treated": "{condition}",
    "evidence_level": "phase_3_trial",
    "overview": "Brief description...",
    "duration_weeks": 12,
    "total_sessions": 8,
    "evidence_sources": ["Study 1", "Study 2"]
  }},
  "steps": [
    {{
      "sequence_order": 1,
      "step_type": "screening",
      "title": "Initial Psychiatric Evaluation",
      "description": "Comprehensive assessment...",
      "duration_minutes": 90,
      "required_roles": ["medical_director"],
      "clinical_scales": ["MADRS", "BDI-II"],
      "vitals_monitoring": {{"heart_rate": true, "blood_pressure": true}}
    }}
  ],
  "safety_checks": [
    {{
      "step_sequence": 1,
      "check_type": "absolute_contraindication",
      "condition": {{"field": "medical_history", "contains": "active_psychosis"}},
      "severity": "blocking",
      "override_allowed": "false",
      "evidence_source": "FDA guidelines"
    }}
  ]
}}
```

**Important Guidelines:**
- Be conservative: Only extract information explicitly stated in the research
- Use evidence-based dosages and timing
- Flag any safety concerns prominently
- If information is missing, use null or omit the field
- Maintain scientific accuracy and medical precision

Begin extraction:"""


def get_patient_education_prompt(protocol_name: str, condition: str, patient_context: dict) -> str:
    """Generate prompt for creating patient education content.

    Args:
        protocol_name: Name of the treatment protocol
        condition: Condition being treated
        patient_context: Dict with patient info (anxiety_level, age_range, education_level)

    Returns:
        Formatted prompt for Claude API
    """
    anxiety_level = patient_context.get("anxiety_level", "moderate")
    age_range = patient_context.get("age_range", "adult")
    education_level = patient_context.get("education_level", "general")

    return f"""You are a compassionate medical educator specializing in patient communication. Your task is to create personalized educational content about a treatment protocol.

**Protocol:** {protocol_name}
**Condition:** {condition}

**Patient Context:**
- Anxiety Level: {anxiety_level} (low/moderate/high)
- Age Range: {age_range} (young_adult/adult/senior)
- Education Level: {education_level} (general/technical/medical)

**Your Task:**
Create a warm, reassuring "What to Expect" guide that helps the patient understand their treatment journey.

**Content Requirements:**

1. **Introduction** (2-3 paragraphs)
   - Acknowledge their courage in seeking treatment
   - Brief explanation of the protocol in accessible language
   - Realistic but hopeful tone

2. **Timeline Overview**
   - Visual timeline of major phases
   - What happens in each phase
   - Approximate duration

3. **What You'll Experience**
   - Session-by-session breakdown
   - Physical sensations they might notice
   - Emotional experiences (normalized)
   - Support available at each stage

4. **Preparation Tips**
   - Practical steps before treatment
   - Questions to ask their care team
   - How to prepare mentally and physically

5. **Safety and Support**
   - Safety monitoring (reassuring but thorough)
   - Who will be with them
   - 24/7 support contacts
   - Common concerns addressed

6. **After Treatment**
   - Integration phase explained
   - Long-term follow-up
   - Community resources

**Tone Guidance:**
- For HIGH anxiety: Extra reassurance, detailed safety info, normalize concerns
- For MODERATE anxiety: Balanced information, encouraging but realistic
- For LOW anxiety: Straightforward, focus on logistics and empowerment

**Language Level:**
- GENERAL: Avoid medical jargon, use analogies, simple explanations
- TECHNICAL: Some medical terms OK, explain mechanisms
- MEDICAL: Technical precision, clinical terminology

**Format:**
Return the content in Markdown format with:
- Clear headings (##)
- Bullet points for readability
- Callout boxes for important info (> **Note:** ...)
- Empathetic, person-first language
- Length: 1000-1500 words

**Critical Requirements:**
- Never make unrealistic promises about outcomes
- Always emphasize the experimental/investigational nature if applicable
- Include proper disclaimers
- Encourage questions and open communication
- Emphasize safety and professional support

Begin generating the patient education content:"""


def get_clinical_decision_support_prompt(
    session_data: dict,
    protocol_context: dict,
    patient_history: dict
) -> str:
    """Generate prompt for real-time clinical decision support.

    Args:
        session_data: Current session vitals, observations, adverse events
        protocol_context: Current protocol step, safety checks, evaluation rules
        patient_history: Previous sessions, baseline measures, risk factors

    Returns:
        Formatted prompt for Claude API
    """
    return f"""You are a clinical decision support system for psychedelic-assisted therapy. Your role is to analyze session data and provide evidence-based recommendations to the treating clinician.

**CURRENT SESSION DATA:**
```json
{session_data}
```

**PROTOCOL CONTEXT:**
```json
{protocol_context}
```

**PATIENT HISTORY:**
```json
{patient_history}
```

**Your Task:**
Analyze the current clinical situation and provide decision support.

**Analysis Framework:**

1. **Safety Assessment**
   - Review all vital signs against normal ranges
   - Check for adverse events or concerning symptoms
   - Evaluate protocol compliance
   - Assess any contraindications or risk factors

2. **Clinical Progress Evaluation**
   - Compare current measures to baseline
   - Assess trajectory (improving/stable/declining)
   - Review any clinical scales administered
   - Evaluate patient's subjective experience

3. **Decision Point Analysis**
   - If at a protocol decision point, evaluate criteria
   - Determine if continuation criteria are met
   - Assess readiness for next phase
   - Consider dose adjustments if applicable

4. **Risk Stratification**
   - Calculate overall risk level (low/moderate/high/critical)
   - Identify specific risk factors requiring attention
   - Flag any urgent concerns

**Output Format:**
Return a JSON object with this structure:

```json
{{
  "risk_level": "low|moderate|high|critical",
  "risk_factors": [
    {{
      "factor": "Description of concern",
      "severity": "info|warning|urgent",
      "recommendation": "Specific action to take"
    }}
  ],
  "recommendations": [
    {{
      "category": "safety|dosing|monitoring|followup",
      "priority": "high|medium|low",
      "action": "Specific recommendation",
      "rationale": "Evidence-based reasoning",
      "evidence_basis": "Reference to protocol or research"
    }}
  ],
  "decision_point_evaluation": {{
    "meets_continuation_criteria": true,
    "reasons": ["Criterion 1 met", "Criterion 2 met"],
    "suggested_next_step": "Proceed to integration phase"
  }},
  "clinical_notes": "Free-text summary for clinician",
  "requires_immediate_attention": false,
  "suggested_interventions": [
    "Specific clinical interventions if needed"
  ]
}}
```

**Critical Guidelines:**
- **Conservative Approach:** When in doubt, recommend caution
- **Flag Borderline Cases:** Highlight any measurements near threshold values
- **Evidence-Based:** All recommendations must cite protocol or research basis
- **Escalation Awareness:** Know when to recommend medical director consultation
- **Document Everything:** Assume this analysis will be part of medical record
- **Never Override Safety:** Safety checks must always be respected

**Risk Level Criteria:**
- **LOW:** All vitals normal, no adverse events, protocol compliance good
- **MODERATE:** Minor deviations, manageable side effects, requires monitoring
- **HIGH:** Significant concerns, protocol deviations, requires intervention
- **CRITICAL:** Immediate safety risk, urgent medical attention needed

**Important:**
- This is decision SUPPORT, not decision MAKING
- Final clinical judgment rests with the licensed provider
- Focus on actionable, specific recommendations
- Be clear about uncertainty when data is ambiguous
- Always prioritize patient safety

Begin clinical analysis:"""


def get_protocol_validation_prompt(protocol_json: dict) -> str:
    """Generate prompt for validating extracted protocol structure.

    Args:
        protocol_json: Extracted protocol data to validate

    Returns:
        Formatted prompt for Claude API
    """
    return f"""You are a medical protocol quality assurance expert. Review this extracted protocol for completeness, safety, and clinical validity.

**Protocol to Review:**
```json
{protocol_json}
```

**Validation Checklist:**

1. **Completeness:**
   - All required fields present
   - No critical information missing
   - Steps in logical sequence
   - Duration and timing specified

2. **Safety:**
   - Adequate screening procedures
   - Appropriate contraindications
   - Safety monitoring throughout
   - Emergency procedures referenced

3. **Clinical Validity:**
   - Evidence-based dosing
   - Appropriate clinical scales
   - Realistic timelines
   - Proper role assignments

4. **Compliance:**
   - Regulatory requirements addressed
   - Informed consent process
   - Documentation requirements
   - Audit trail considerations

**Output:**
Return a JSON object:

```json
{{
  "is_valid": true,
  "validation_score": 95,
  "critical_issues": [],
  "warnings": [
    "Minor concern description"
  ],
  "suggestions": [
    "Recommendation for improvement"
  ],
  "completeness_check": {{
    "required_fields": true,
    "step_sequence": true,
    "safety_checks": true,
    "evidence_sources": false
  }}
}}
```

Begin validation:"""

from dotenv import load_dotenv

from educhain.models import ChatModel
from educhain.prompts import PromptTemplate
from educhain.output_parsers import StringOutputParser
from educhain.core import RunnableParallel

load_dotenv()

# -------------------------------------------------------
# Shared Components
# -------------------------------------------------------

llm = ChatModel()
parser = StringOutputParser()

# -------------------------------------------------------
# Chain 1 : Market Analysis
# -------------------------------------------------------

market_prompt = PromptTemplate(
    template="""
You are an experienced startup consultant.

Analyze the market opportunity for the following startup idea.

Startup Idea:
{idea}

Give:
- Market demand
- Existing competitors
- Future potential

Keep it concise.
""",
    input_variables=["idea"]
)

market_chain = market_prompt | llm | parser


# -------------------------------------------------------
# Chain 2 : Target Audience
# -------------------------------------------------------

audience_prompt = PromptTemplate(
    template="""
Identify the target audience for the following startup.

Startup Idea:
{idea}

Mention:

- Primary users
- Secondary users
- Customer pain points

Keep it practical.
""",
    input_variables=["idea"]
)

audience_chain = audience_prompt | llm | parser


# -------------------------------------------------------
# Chain 3 : Monetization
# -------------------------------------------------------

money_prompt = PromptTemplate(
    template="""
Suggest a business model for this startup.

Startup Idea:
{idea}

Include:

- Revenue model
- Pricing strategy
- Subscription ideas
- Additional income sources

Keep it realistic.
""",
    input_variables=["idea"]
)

money_chain = money_prompt | llm | parser


# -------------------------------------------------------
# Chain 4 : MVP Features
# -------------------------------------------------------

mvp_prompt = PromptTemplate(
    template="""
You are a product manager.

Suggest the MVP (Minimum Viable Product) for this startup.

Startup Idea:
{idea}

List only the essential features.

Avoid unnecessary complexity.
""",
    input_variables=["idea"]
)

mvp_chain = mvp_prompt | llm | parser


# -------------------------------------------------------
# Chain 5 : Risks
# -------------------------------------------------------

risk_prompt = PromptTemplate(
    template="""
Analyze the biggest risks for the following startup.

Startup Idea:
{idea}

Discuss:

- Technical risks
- Business risks
- Competition
- Scaling challenges

Keep it practical.
""",
    input_variables=["idea"]
)

risk_chain = risk_prompt | llm | parser


# -------------------------------------------------------
# RunnableParallel
# -------------------------------------------------------

startup_analyzer = RunnableParallel(
    market_analysis=market_chain,
    target_audience=audience_chain,
    monetization=money_chain,
    mvp_features=mvp_chain,
    risks=risk_chain,
)


# -------------------------------------------------------
# User Input
# -------------------------------------------------------

idea = {
    "idea": "AI-powered Resume Analyzer for Students using Large Language Models"
}


# -------------------------------------------------------
# Execute
# -------------------------------------------------------

results = startup_analyzer.invoke(idea)


# -------------------------------------------------------
# Display
# -------------------------------------------------------

print("\n" + "=" * 70)
print("🚀 AI STARTUP IDEA ANALYZER")
print("=" * 70)

print("\n💡 Startup Idea:")
print(idea["idea"])


print("\n" + "-" * 70)
print("📈 Market Analysis")
print("-" * 70)
print(results["market_analysis"])


print("\n" + "-" * 70)
print("🎯 Target Audience")
print("-" * 70)
print(results["target_audience"])


print("\n" + "-" * 70)
print("💰 Monetization Strategy")
print("-" * 70)
print(results["monetization"])


print("\n" + "-" * 70)
print("🚀 MVP Features")
print("-" * 70)
print(results["mvp_features"])


print("\n" + "-" * 70)
print("⚠ Risks & Challenges")
print("-" * 70)
print(results["risks"])

print("\n" + "=" * 70)
print("✅ Analysis Completed Successfully")
print("=" * 70)
"""
Discord Bot Optimized with Groq LLM Integration
Uses Groq's fast LLM API for intelligent test case generation
"""

import discord
from discord import app_commands
import json
import os
from datetime import datetime
from typing import Optional
import asyncio
import time
from dotenv import load_dotenv
load_dotenv()


class FraudQABot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
    
    async def setup_hook(self):
        await self.tree.sync()

bot = FraudQABot()

@bot.event
async def on_ready():
    groq_status = "✅ ENABLED" if os.getenv('GROQ_API_KEY') else "❌ DISABLED (using rule-based)"
    print(f'✅ {bot.user} is now online!')
    print(f'📊 Fraud QA Bot ready in {len(bot.guilds)} server(s)')
    print(f'🤖 Groq LLM: {groq_status}')

# ============================================
# COMMAND 1: Run QA with Groq LLM
# ============================================
@bot.tree.command(
    name="run-qa",
    description="🔍 Run fraud detection QA tests (uses Groq LLM if available)"
)
@app_commands.describe(
    quick="Run quick test with fewer scenarios (faster)",
    use_groq="Force use of Groq LLM for test generation (default: auto)"
)
async def run_qa(
    interaction: discord.Interaction,
    quick: bool = False,
    use_groq: Optional[bool] = None
):
    """Run QA test with Groq-powered test generation"""
    
    # Check Groq status
    groq_available = bool(os.getenv('GROQ_API_KEY'))
    
    if use_groq and not groq_available:
        await interaction.response.send_message(
            "❌ **Groq LLM not available!**\n\n"
            "Set `GROQ_API_KEY` environment variable to enable Groq.\n"
            "Get your key from: https://console.groq.com",
            ephemeral=True
        )
        return
    
    # Initial response
    groq_status = "🤖 with Groq LLM" if groq_available else "📋 rule-based"
    await interaction.response.send_message(
        f"🚀 **Starting QA Test Suite {groq_status}...**\n"
        "⏳ This may take 1-3 minutes. I'll update you on progress!"
    )
    
    try:
        # Configure based on quick mode
        if quick:
            fraud_types = ['wire_transfer_fraud', 'card_fraud']
            test_count = "15-20"
            compliance = ['PCI_DSS']
        else:
            fraud_types = [
                'wire_transfer_fraud',
                'account_takeover', 
                'card_fraud',
                'identity_theft',
                'money_laundering'
            ]
            test_count = "40-60"
            compliance = ['AML_KYC', 'PCI_DSS', 'GDPR']
        
        requirements = {
            'fraud_types': fraud_types,
            'detection_rules': {
                'high_value_threshold': 10000,
                'velocity_check_window': 3600,
                'geographic_risk_countries': ['NG', 'RU', 'CN'],
                'max_failed_logins': 3
            },
            'compliance_requirements': compliance,
            'performance_requirements': {
                'max_response_time_ms': 5000,
                'min_throughput_tps': 1000
            }
        }
        
        # Update: Initializing
        await interaction.edit_original_response(
            content=f"🚀 **QA Test Running {groq_status}...**\n"
                    "📋 Step 1/3: Initializing agent...\n"
                    "⏳ 10% complete"
        )
        
        # Import here to avoid circular imports
        from fraud_qa_agent import FraudQAAgent
        
        # Initialize agent
        agent = FraudQAAgent()
        
        # Update: Generating with Groq
        if groq_available:
            await interaction.edit_original_response(
                content="🚀 **QA Test Running...**\n"
                        f"🤖 Step 2/3: Generating test cases with Groq LLM ({test_count} tests)...\n"
                        "⏳ 30% complete\n\n"
                        "*Groq is thinking... this takes 2-5 seconds*"
            )
        else:
            await interaction.edit_original_response(
                content="🚀 **QA Test Running...**\n"
                        f"📋 Step 2/3: Generating test cases ({test_count} tests)...\n"
                        "⏳ 30% complete"
            )
        
        # Run the FULL QA cycle - uses Groq if available
        start_time = time.time()
        
        report = agent.run_full_qa_cycle(requirements)
        
        execution_time = time.time() - start_time
        
        # Export results
        agent.export_results('fraud_qa_results.json')
        
        # Build embeds
        embeds = build_qa_embeds(report, groq_available)
        
        # Get test count from report
        test_cases_run = len(agent.test_cases) if hasattr(agent, 'test_cases') else 'Unknown'
        
        # Final response
        mode_text = "⚡ Quick Mode" if quick else "📊 Full Mode"
        llm_text = " (Groq LLM)" if groq_available else " (Rule-Based)"
        
        await interaction.edit_original_response(
            content=f"✅ **QA Test Complete!** {mode_text}{llm_text}\n"
                    f"Tested **{test_cases_run}** scenarios across **{len(fraud_types)}** fraud type(s)\n"
                    f"⏱️ Total time: {execution_time:.1f}s",
            embeds=embeds
        )
        
    except Exception as e:
        # Better error reporting
        import traceback
        error_msg = str(e)
        error_trace = traceback.format_exc()
        
        await interaction.edit_original_response(
            content=f"❌ **Error during QA test:**\n```\n{error_msg}\n```\n"
                    f"*Check bot logs for details*"
        )
        
        # Log full error for debugging
        print(f"\n{'='*60}")
        print(f"ERROR in /run-qa command:")
        print(f"{'='*60}")
        print(error_trace)
        print(f"{'='*60}\n")

# ============================================
# COMMAND 2: Quick Status Check
# ============================================
@bot.tree.command(
    name="qa-status",
    description="📊 View latest results (instant)"
)
async def qa_status(interaction: discord.Interaction):
    """Get latest status - instant response"""
    
    try:
        # Check if results file exists
        if not os.path.exists('fraud_qa_results.json'):
            await interaction.response.send_message(
                "❌ **No QA results found!**\n\n"
                "Run `/run-qa quick:True` to generate results first.",
                ephemeral=True
            )
            return
        
        # Load results
        try:
            with open('fraud_qa_results.json', 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            await interaction.response.send_message(
                "❌ **Results file is corrupted!**\n\n"
                "Run `/run-qa quick:True` to generate new results.",
                ephemeral=True
            )
            return
        
        # Extract data safely
        deployment_rec = data.get('deployment_recommendation', 'Unknown')
        timestamp = data.get('timestamp', 'Unknown')
        
        # Determine color
        if '✅' in deployment_rec:
            color = discord.Color.green()
        elif '⚠️' in deployment_rec:
            color = discord.Color.orange()
        elif '🛑' in deployment_rec or '❌' in deployment_rec:
            color = discord.Color.red()
        else:
            color = discord.Color.blue()
        
        # Create embed
        embed = discord.Embed(
            title="📊 Latest QA Status",
            description=deployment_rec,
            color=color
        )
        
        # Add timestamp
        try:
            if timestamp != 'Unknown':
                embed.timestamp = datetime.fromisoformat(timestamp)
        except:
            pass
        
        # Add test results
        if 'test_results' in data and data['test_results']:
            results = data['test_results']
            passed = sum(1 for r in results if r.get('status') == 'PASSED')
            failed = sum(1 for r in results if r.get('status') == 'FAILED')
            total = len(results)
            
            if total > 0:
                pass_rate = passed / total * 100
                embed.add_field(
                    name="📊 Test Results",
                    value=(
                        f"✅ Passed: {passed}\n"
                        f"❌ Failed: {failed}\n"
                        f"📈 Pass Rate: {pass_rate:.1f}%"
                    ),
                    inline=True
                )
        
        # Add risk assessment
        if 'risk_assessment' in data and data['risk_assessment']:
            risk = data['risk_assessment']
            risk_level = risk.get('risk_level', 'Unknown')
            risk_score = risk.get('overall_risk_score', 0)
            
            risk_emoji = {
                'LOW': '🟢',
                'MEDIUM': '🟡',
                'HIGH': '🟠',
                'CRITICAL': '🔴'
            }.get(risk_level, '⚪')
            
            embed.add_field(
                name="⚠️ Risk Assessment",
                value=f"{risk_emoji} **{risk_level}**\n{risk_score:.1f}/100",
                inline=True
            )
        
        # Show if Groq was used
        groq_used = data.get('groq_used', False)
        if groq_used:
            embed.set_footer(text="🤖 Tests generated with Groq LLM | /run-qa for new tests")
        else:
            embed.set_footer(text="📋 Rule-based tests | /run-qa for new tests")
        
        await interaction.response.send_message(embed=embed)
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        
        await interaction.response.send_message(
            f"❌ **Error loading QA status:**\n```\n{str(e)}\n```\n"
            f"Try running `/run-qa quick:True` to generate new results.",
            ephemeral=True
        )
        
        print(f"\n{'='*60}")
        print(f"ERROR in /qa-status command:")
        print(f"{'='*60}")
        print(error_trace)
        print(f"{'='*60}\n")

# ============================================
# COMMAND 3: Check Groq Status
# ============================================
@bot.tree.command(
    name="groq-status",
    description="🤖 Check if Groq LLM is available"
)
async def groq_status(interaction: discord.Interaction):
    """Check Groq LLM status"""
    
    groq_key = os.getenv('GROQ_API_KEY')
    
    if groq_key:
        embed = discord.Embed(
            title="🤖 Groq LLM Status",
            description="✅ **Groq is ENABLED**",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="API Key",
            value=f"Set (length: {len(groq_key)} chars)",
            inline=True
        )
        
        embed.add_field(
            name="Model",
            value="llama-3.3-70b-versatile",
            inline=True
        )
        
        embed.add_field(
            name="Speed",
            value="~750 tokens/second",
            inline=True
        )
        
        embed.add_field(
            name="Benefits",
            value=(
                "✅ Smarter test cases\n"
                "✅ More edge cases\n"
                "✅ Adversarial scenarios\n"
                "✅ Realistic fraud patterns"
            ),
            inline=False
        )
        
        embed.set_footer(text="Test generation will use Groq LLM")
        
    else:
        embed = discord.Embed(
            title="🤖 Groq LLM Status",
            description="❌ **Groq is DISABLED**",
            color=discord.Color.red()
        )
        
        embed.add_field(
            name="Current Mode",
            value="📋 Rule-based test generation",
            inline=False
        )
        
        embed.add_field(
            name="To Enable Groq",
            value=(
                "1. Get API key from: https://console.groq.com\n"
                "2. Set environment variable: `GROQ_API_KEY`\n"
                "3. Restart the bot"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Why Enable?",
            value=(
                "🧠 Smarter test cases\n"
                "🎯 Better edge case coverage\n"
                "🔄 Different tests each run\n"
                "💰 Free tier available"
            ),
            inline=False
        )
        
        embed.set_footer(text="Bot will work fine without Groq (rule-based mode)")
    
    await interaction.response.send_message(embed=embed)

# ============================================
# COMMAND 4: Risk Assessment
# ============================================
@bot.tree.command(
    name="risk",
    description="⚠️ Quick risk assessment (instant)"
)
async def risk(interaction: discord.Interaction):
    """Quick risk view"""
    
    try:
        if not os.path.exists('fraud_qa_results.json'):
            await interaction.response.send_message(
                "❌ **No QA results found!**\n\n"
                "Run `/run-qa quick:True` to generate results first.",
                ephemeral=True
            )
            return
        
        with open('fraud_qa_results.json', 'r') as f:
            data = json.load(f)
        
        risk = data.get('risk_assessment')
        
        if not risk:
            await interaction.response.send_message(
                "❌ **No risk data available!**\n\n"
                "The results file may be incomplete. Run `/run-qa quick:True` to regenerate.",
                ephemeral=True
            )
            return
        
        score = risk.get('overall_risk_score', 0)
        level = risk.get('risk_level', 'UNKNOWN')
        
        colors = {
            'LOW': discord.Color.green(),
            'MEDIUM': discord.Color.gold(),
            'HIGH': discord.Color.orange(),
            'CRITICAL': discord.Color.red()
        }
        
        emojis = {
            'LOW': '🟢',
            'MEDIUM': '🟡',
            'HIGH': '🟠',
            'CRITICAL': '🔴'
        }
        
        embed = discord.Embed(
            title=f"{emojis.get(level, '⚪')} Risk Assessment: {level}",
            description=f"**Overall Score: {score:.1f}/100**",
            color=colors.get(level, discord.Color.blue())
        )
        
        embed.add_field(
            name="🔍 Detection Risk", 
            value=f"{risk.get('detection_risk', 0):.0f}/100", 
            inline=True
        )
        embed.add_field(
            name="⚡ False Positive Risk", 
            value=f"{risk.get('false_positive_risk', 0):.0f}/100", 
            inline=True
        )
        embed.add_field(
            name="📋 Compliance Risk", 
            value=f"{risk.get('compliance_risk', 0):.0f}/100", 
            inline=True
        )
        embed.add_field(
            name="🖥️ System Risk", 
            value=f"{risk.get('system_risk', 0):.0f}/100", 
            inline=True
        )
        
        embed.set_footer(text="Use /qa-status for full details")
        
        await interaction.response.send_message(embed=embed)
        
    except Exception as e:
        await interaction.response.send_message(
            f"❌ **Error:** {str(e)}\n\nRun `/run-qa quick:True` to regenerate results.",
            ephemeral=True
        )

# ============================================
# COMMAND 5: Help
# ============================================
@bot.tree.command(
    name="help",
    description="❓ Show all commands and Groq status"
)
async def help_command(interaction: discord.Interaction):
    """Show help"""
    
    groq_available = bool(os.getenv('GROQ_API_KEY'))
    groq_emoji = "✅" if groq_available else "❌"
    
    embed = discord.Embed(
        title="🤖 Fraud QA Bot Commands",
        description=f"**Groq LLM:** {groq_emoji} {'Enabled' if groq_available else 'Disabled'}\n\n"
                    "Choose based on your needs:",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="⚡ `/run-qa quick:True`",
        value="Fast test (~15-20 tests, 1-2 min) ⭐ **Recommended**",
        inline=False
    )
    
    embed.add_field(
        name="📊 `/run-qa`",
        value="Full test (~40-60 tests, 3-5 min)",
        inline=False
    )
    
    embed.add_field(
        name="📈 `/qa-status`",
        value="View last results (instant)",
        inline=False
    )
    
    embed.add_field(
        name="⚠️ `/risk`",
        value="Quick risk check (instant)",
        inline=False
    )
    
    embed.add_field(
        name="🤖 `/groq-status`",
        value="Check if Groq LLM is enabled",
        inline=False
    )
    
    embed.add_field(
        name="❓ `/help`",
        value="Show this message",
        inline=False
    )
    
    if groq_available:
        embed.add_field(
            name="🤖 Groq LLM Benefits",
            value="✅ Smarter test cases\n✅ Better edge coverage\n✅ Adversarial scenarios",
            inline=False
        )
    else:
        embed.add_field(
            name="💡 Enable Groq LLM",
            value="Get API key: https://console.groq.com\nSet: `GROQ_API_KEY` environment variable",
            inline=False
        )
    
    embed.set_footer(text="💡 Tip: Use 'quick:True' for faster results!")
    
    await interaction.response.send_message(embed=embed)

# ============================================
# Helper Functions
# ============================================

def build_qa_embeds(report, groq_used=False):
    """Build embeds from report"""
    
    try:
        exec_summary = report.get('executive_summary', {})
        
        # Determine color based on deployment recommendation
        deployment_rec = exec_summary.get('deployment_recommendation', 'Unknown')
        if '✅' in deployment_rec:
            color = discord.Color.green()
        elif '⚠️' in deployment_rec:
            color = discord.Color.orange()
        else:
            color = discord.Color.red()
        
        # Title shows if Groq was used
        title_suffix = " (Groq LLM)" if groq_used else " (Rule-Based)"
        
        embed = discord.Embed(
            title=f"🔍 QA Test Results{title_suffix}",
            description=f"**Status:** {exec_summary.get('overall_status', 'Unknown')}",
            color=color,
            timestamp=datetime.now()
        )
        
        # Add metrics if available
        metrics = exec_summary.get('key_metrics', {})
        if metrics:
            embed.add_field(
                name="📊 Results",
                value=(
                    f"✅ Pass: **{metrics.get('pass_rate', 'N/A')}**\n"
                    f"🎯 Accuracy: **{metrics.get('fraud_detection_accuracy', 'N/A')}**\n"
                    f"⚠️ FP Rate: **{metrics.get('false_positive_rate', 'N/A')}**"
                ),
                inline=True
            )
        
        # Add critical issues
        critical_issues = exec_summary.get('critical_issues', 0)
        embed.add_field(
            name="🚨 Issues",
            value=f"**{critical_issues}** critical",
            inline=True
        )
        
        # Add deployment recommendation
        embed.add_field(
            name="🚀 Deployment",
            value=deployment_rec,
            inline=False
        )
        
        # Add top insights if available
        top_insights = exec_summary.get('top_insights', [])
        if top_insights:
            insights = "\n".join(f"• {i[:80]}" for i in top_insights[:3])
            embed.add_field(
                name="💡 Insights",
                value=insights if insights else "No insights available",
                inline=False
            )
        
        # Footer indicates generation method
        if groq_used:
            embed.set_footer(text="🤖 Tests generated with Groq LLM | llama-3.3-70b-versatile")
        else:
            embed.set_footer(text="📋 Rule-based test generation | Enable Groq for smarter tests")
        
        return [embed]
        
    except Exception as e:
        # If there's an error building the embed, return error embed
        error_embed = discord.Embed(
            title="❌ Error Building Report",
            description=f"Error: {str(e)}",
            color=discord.Color.red()
        )
        error_embed.add_field(
            name="Debug Info",
            value=f"Available keys: {', '.join(report.keys())}",
            inline=False
        )
        return [error_embed]

# ============================================
# Run Bot
# ============================================

if __name__ == "__main__":
    import sys
    
    # Check for bot token
    BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
    
    if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("❌ Please set your Discord bot token!")
        print("   Option 1: Set environment variable: export DISCORD_BOT_TOKEN='your_token'")
        print("   Option 2: Edit this file and replace 'YOUR_BOT_TOKEN_HERE'")
        sys.exit(1)
    
    # Check Groq status
    groq_key = os.getenv('GROQ_API_KEY')
    
    print("🚀 Starting Optimized Fraud QA Bot with Groq Integration...")
    print("="*60)
    print("💡 Features:")
    print("   • Progress updates during tests")
    print("   • Quick mode for fast results")
    print("   • Real-time risk assessment")
    print(f"   • Groq LLM: {'✅ ENABLED' if groq_key else '❌ DISABLED (rule-based)'}")
    print()
    
    if not groq_key:
        print("ℹ️  Groq LLM is not enabled (bot will use rule-based generation)")
        print("   To enable Groq:")
        print("   1. Get API key from: https://console.groq.com")
        print("   2. export GROQ_API_KEY='gsk_...'")
        print("   3. Restart bot")
        print()
    
    print("="*60)
    
    try:
        bot.run(BOT_TOKEN)
    except Exception as e:
        print(f"\n❌ Error starting bot: {e}")
        sys.exit(1)
import logfire
from langchain_groq import ChatGroq
from nemoguardrails import RailsConfig, LLMRails

from app.config import settings
from app.guardrails.colang_rules import (
    COLANG_CONTENT,
    YAML_CONTENT,
    RAIL_INDICATORS,
    match_conversation_rail,
)
from app.guardrails.security import security_gate
from app.guardrails.security_model import guard_llm


_rails: LLMRails | None = None


def initialize_rails() -> None:
    """
    Build the NeMo LLMRails singleton at app startup.

    NeMo is responsible only for conversational rails
    (greetings, farewells, capabilities).

    Security checks are handled separately by SecurityGate.
    """
    global _rails


    """
    guard_llm = ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model="llama-3.1-8b-instant",
        temperature=0,
    )"""

    config = RailsConfig.from_content(
        colang_content=COLANG_CONTENT,
        yaml_content=YAML_CONTENT,
    )

    _rails = LLMRails(
        config=config,
        llm=guard_llm,
    )

    logfire.info(
        "🛡️ NeMo Guardrails initialised (llama-3.1-8b-instant)."
    )


def guard(message: str) -> tuple[bool, str | None]:
    """
    Security + NeMo conversation gate.

    Returns:
        (True, response)
            A security policy or NeMo conversational rail fired.
            Return the response immediately and skip the RAG pipeline.

        (False, None)
            Message is allowed to continue into LangGraph.
    """

    # ------------------------------------------------------------------
    # Conversational Rails (before security — greetings are off-topic to
    # the security classifier and would be blocked before NeMo runs)
    # ------------------------------------------------------------------

    canned = match_conversation_rail(message)
    if canned is not None:
        logfire.info(
            f"🛡️ Conversation rail fired (pattern) | query='{message[:80]}'"
        )
        return True, canned

    if _rails is not None:
        with logfire.span("🛡️ NeMo Conversation Rails"):
            result = _rails.generate(
                messages=[{"role": "user", "content": message}]
            )

            content = (
                result.get("content", "")
                if isinstance(result, dict)
                else str(result)
            )

            fired = any(indicator in content for indicator in RAIL_INDICATORS)

            if fired:
                logfire.info(
                    f"🛡️ Conversation rail fired (NeMo) | query='{message[:80]}'"
                )
                return True, content

            logfire.info("✅ NeMo conversation rails passed.")
    else:
        logfire.warning(
            "⚠️ Guardrails not initialised — skipping NeMo rails."
        )

    # ------------------------------------------------------------------
    # Security Checks
    # ------------------------------------------------------------------

    with logfire.span("🔒 Security Check"):

        security = security_gate.check(message)

        if security.prompt_injection:

            logfire.info(
                f"🚫 Prompt Injection blocked | query='{message[:80]}'"
            )

            return (
                True,
                (
                    "I can't change my identity or ignore my instructions. "
                    "I'm here to help with Kubernetes and cloud-native topics."
                ),
            )

        if security.prompt_leakage:

            logfire.info(
                f"🚫 Prompt Leakage blocked | query='{message[:80]}'"
            )

            return (
                True,
                (
                    "I can't reveal my internal prompts, instructions, "
                    "guardrails, or system configuration."
                ),
            )

        if not security.topic_allowed:

            logfire.info(
                f"🚫 Off-topic request blocked | query='{message[:80]}'"
            )

            return (
                True,
                (
                    "I'm an AI Assistant specialising in Kubernetes and "
                    "cloud-native technologies. "
                    "Please ask me a Kubernetes-related question."
                ),
            )

        logfire.info("✅ Security checks passed.")

    return False, None
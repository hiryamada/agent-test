"""Research and analyze public reviews of a book with Microsoft Foundry."""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence

def build_review_prompt(title: str, author: str | None = None) -> str:
    """Build a Japanese research prompt for the specified book."""
    book = f"「{title}」"
    if author:
        book += f"（著者: {author}）"
    return (
        f"{book}について、ウェブ上で公開されている読者レビューを調査してください。"
        "可能な限り複数の独立した情報源からレビューを集め、次の項目を日本語で分析してください。\n"
        "1. 調査したレビューと情報源の概要（レビュー件数が分かる場合は件数も記載）\n"
        "2. 全体的な評価や肯定・否定の傾向\n"
        "3. 読者が評価している点と批判している点、それぞれの主なテーマ\n"
        "4. どのような読者に向いているか\n"
        "5. 調査の限界やレビューの偏り\n\n"
        "実際に確認できた情報だけを使い、レビュー内容や件数を捏造しないでください。"
        "事実と分析上の推測を区別し、参照した情報源を回答内で引用してください。"
        "同名の書籍がある場合は、著者や出版情報を確認して対象を特定してください。"
    )


def _required_environment(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"環境変数 {name} を設定してください。")
    return value


def _render_response(message: object) -> str:
    """Return the agent text with web citations rendered as Markdown links."""
    responses = [
        text_message.text.value
        for text_message in message.text_messages  # type: ignore[attr-defined]
    ]
    response = "\n".join(responses)
    for annotation in message.url_citation_annotations:  # type: ignore[attr-defined]
        citation = annotation.url_citation
        response = response.replace(
            annotation.text, f"[{citation.title}]({citation.url})"
        )
    return response


def analyze_book(title: str, author: str | None = None) -> str:
    endpoint = _required_environment("PROJECT_ENDPOINT")
    deployment = _required_environment("MODEL_DEPLOYMENT_NAME")
    connection_name = _required_environment("BING_CONNECTION_NAME")

    from azure.ai.agents.models import BingGroundingTool, MessageRole
    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential

    credential = DefaultAzureCredential()
    project_client = AIProjectClient(endpoint=endpoint, credential=credential)
    agent = None
    try:
        with project_client:
            try:
                connection_id = project_client.connections.get(connection_name).id
                bing = BingGroundingTool(connection_id=connection_id)
                agents_client = project_client.agents
                agent = agents_client.create_agent(
                    model=deployment,
                    name="book-review-researcher",
                    instructions=(
                        "あなたは書籍レビューの調査・分析アシスタントです。"
                        "ウェブ検索で確認した公開情報に基づいて回答し、情報源を明示してください。"
                    ),
                    tools=bing.definitions,
                )
                thread = agents_client.threads.create()
                agents_client.messages.create(
                    thread_id=thread.id,
                    role=MessageRole.USER,
                    content=build_review_prompt(title, author),
                )
                run = agents_client.runs.create_and_process(
                    thread_id=thread.id, agent_id=agent.id
                )
                if run.status != "completed":
                    detail = f": {run.last_error}" if run.last_error else ""
                    raise RuntimeError(f"エージェントの実行に失敗しました{detail}")

                message = agents_client.messages.get_last_message_by_role(
                    thread_id=thread.id, role=MessageRole.AGENT
                )
                if message is None:
                    raise RuntimeError("エージェントから回答を取得できませんでした。")
                return _render_response(message)
            finally:
                if agent is not None:
                    project_client.agents.delete_agent(agent.id)
    finally:
        credential.close()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Microsoft Foundryで指定した書籍の口コミを調査・分析します。"
    )
    parser.add_argument("title", help="調査する書籍のタイトル")
    parser.add_argument("--author", help="著者名（同名書籍の特定に使用）")
    args = parser.parse_args(argv)
    if not args.title.strip():
        parser.error("書籍タイトルを空にはできません。")

    try:
        print(analyze_book(args.title.strip(), args.author.strip() if args.author else None))
    except (ValueError, RuntimeError) as error:
        print(f"エラー: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

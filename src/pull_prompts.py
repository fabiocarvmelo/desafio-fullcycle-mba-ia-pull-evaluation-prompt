"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
import yaml
from dotenv import load_dotenv
from langchain import hub

load_dotenv()


# Configura o PyYAML para usar o estilo '|' em strings multilinhas
class CustomYamlDumper(yaml.SafeDumper):
    pass


def custom_str_representer(dumper, data):
    # Se a string tiver quebras de linha, usa o estilo de bloco '|'
    if "\n" in data:
        clean_data = data.rstrip() + "\n"
        return dumper.represent_scalar("tag:yaml.org,2002:str", clean_data, style="|")
    
    # Para strings simples específicas, força aspas duplas
    if data.startswith("{") or "Prompt para" in data or data in ["v1", "2025-01-15"]:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')
        
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


CustomYamlDumper.add_representer(str, custom_str_representer)


def pull_prompts_from_langsmith():
    """Puxa o prompt do Hub e salva no formato YAML exato de referência"""
    Path("prompts").mkdir(parents=True, exist_ok=True)

    # Faz o pull do prompt do Hub
    prompt = hub.pull("leonanluppi/bug_to_user_story_v1")

    system_prompt_text = prompt.messages[0].prompt.template
    user_prompt_text = prompt.messages[1].prompt.template

    prompt_data = {
        "bug_to_user_story_v1": {
            "description": "Prompt para converter relatos de bugs em User Stories",
            "system_prompt": system_prompt_text,
            "user_prompt": user_prompt_text,
            "version": "v1",
            "created_at": "2025-01-15",
            "tags": ["bug-analysis", "user-story", "product-management"],
        }
    }

    # Cabeçalho de comentários
    header_comment = (
        "# Este arquivo contém o prompt inicial de BAIXA QUALIDADE que você deve otimizar.\n"
        "# Os problemas são intencionais (ex: {bug_report} duplicado no system e user prompt,\n"
        "# instruções vagas, falta de exemplos, sem persona definida).\n"
        "# Use-o como base para entender o que precisa ser melhorado na v2.\n\n"
    )

    nome_arquivo_prompt = "prompts/bug_to_user_story_v1.yml"

    # Gera a string YAML na memória primeiro
    yaml_text = yaml.dump(
        prompt_data,
        Dumper=CustomYamlDumper,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=None,
    )

    # Injeta o comentário de metadados antes da linha da versão
    yaml_text = yaml_text.replace("  version:", "  # Metadados\n  version:")

    with open(nome_arquivo_prompt, "w", encoding="utf-8") as f:
        f.write(header_comment)
        f.write(yaml_text)

    print(f"Prompt salvo com sucesso em {nome_arquivo_prompt}")


def main():
    pull_prompts_from_langsmith()


if __name__ == "__main__":
    sys.exit(main())

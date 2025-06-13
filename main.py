from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import ast
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8100"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodigoRequest(BaseModel):
    codigo: str
    lenguaje: str

def run_subprocess(command, input_text):
    try:
        result = subprocess.run(command, input=input_text.encode(), capture_output=True, timeout=5)
        return result.returncode, result.stdout.decode(), result.stderr.decode()
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout expired"

@app.post("/analizar-codigo")
def analizar_codigo(data: CodigoRequest):
    codigo = data.codigo
    lenguaje = data.lenguaje.strip().lower()

    if lenguaje == "python":
        try:
            ast.parse(codigo)
            return {"lenguaje": lenguaje, "valido": True, "mensaje": "Código Python válido."}
        except SyntaxError as e:
            return {"lenguaje": lenguaje, "valido": False, "mensaje": f"Error de sintaxis en Python: {str(e)}"}

    elif lenguaje == "javascript":
        returncode, stdout, stderr = run_subprocess(["node", "--check"], codigo)
        if returncode == 0:
            return {"lenguaje": lenguaje, "valido": True, "mensaje": "Código JavaScript válido."}
        else:
            return {"lenguaje": lenguaje, "valido": False, "mensaje": stderr}

    elif lenguaje == "typescript":
        returncode, stdout, stderr = run_subprocess(["tsc", "--noEmit", "-"], codigo)
        return {"lenguaje": lenguaje, "valido": returncode == 0, "mensaje": stderr or "Código TypeScript válido."}

    elif lenguaje == "java":
        if re.search(r"public\\s+class\\s+\\w+", codigo):
            return {"lenguaje": lenguaje, "valido": True, "mensaje": "Clase Java válida (validación básica)."}
        return {"lenguaje": lenguaje, "valido": False, "mensaje": "No se detecta clase Java válida."}

    elif lenguaje == "swift":
        if "func" in codigo:
            return {"lenguaje": lenguaje, "valido": True, "mensaje": "Código Swift válido (validación básica)."}
        return {"lenguaje": lenguaje, "valido": False, "mensaje": "No se detectaron funciones Swift."}

    elif lenguaje == "sql":
        keywords = ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP"]
        if any(word in codigo.upper() for word in keywords):
            return {"lenguaje": lenguaje, "valido": True, "mensaje": "Código SQL válido (validación básica)."}
        return {"lenguaje": lenguaje, "valido": False, "mensaje": "Código SQL inválido o sin palabras clave."}

    elif lenguaje == "rust":
        returncode, stdout, stderr = run_subprocess(["rustc", "--emit=metadata", "-"], codigo)
        return {"lenguaje": lenguaje, "valido": returncode == 0, "mensaje": stderr or "Código Rust válido."}

    elif lenguaje == "ruby":
        returncode, stdout, stderr = run_subprocess(["ruby", "-c"], codigo)
        return {"lenguaje": lenguaje, "valido": "Syntax OK" in stdout, "mensaje": stderr or stdout}

    elif lenguaje == "php":
        if "<?php" not in codigo:
            return {"lenguaje": lenguaje, "valido": False, "mensaje": "El código PHP debe incluir la etiqueta <?php"}
        returncode, stdout, stderr = run_subprocess(["php", "-l"], codigo)
        return {
        "lenguaje": lenguaje,
        "valido": "No syntax errors detected" in stdout,
        "mensaje": stderr or stdout
    }

    elif lenguaje == "kotlin":
        if "fun " in codigo:
            return {"lenguaje": lenguaje, "valido": True, "mensaje": "Código Kotlin válido (validación básica)."}
        return {"lenguaje": lenguaje, "valido": False, "mensaje": "No se detectaron funciones Kotlin."}

    elif lenguaje == "html":
        if re.search(r"<\\s*html.*?>", codigo, re.IGNORECASE):
            return {"lenguaje": lenguaje, "valido": True, "mensaje": "Código HTML válido (validación básica)."}
        return {"lenguaje": lenguaje, "valido": False, "mensaje": "No se detectó etiqueta HTML."}

    elif lenguaje == "go":
        returncode, stdout, stderr = run_subprocess(["go", "vet"], codigo)
        return {"lenguaje": lenguaje, "valido": returncode == 0, "mensaje": stderr or "Código Go válido."}

    elif lenguaje == "css":
        if re.search(r"\\s*[a-zA-Z0-9\\-]+\\s*{", codigo):
            return {"lenguaje": lenguaje, "valido": True, "mensaje": "Código CSS válido (validación básica)."}
        return {"lenguaje": lenguaje, "valido": False, "mensaje": "Código CSS inválido."}

    elif lenguaje == "c++":
        returncode, stdout, stderr = run_subprocess(["g++", "-fsyntax-only", "-"], codigo)
        return {"lenguaje": lenguaje, "valido": returncode == 0, "mensaje": stderr or "Código C++ válido."}

    elif lenguaje == "c#":
        if re.search(r"class\\s+\\w+", codigo):
            return {"lenguaje": lenguaje, "valido": True, "mensaje": "Código C# válido (validación básica)."}
        return {"lenguaje": lenguaje, "valido": False, "mensaje": "No se detectó clase en C#."}

    else:
        return {"lenguaje": lenguaje, "valido": False, "mensaje": f"Lenguaje '{lenguaje}' no soportado."}

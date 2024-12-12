import subprocess

def start_game(username, version, ram):
    java_path = "java"  # Ruta al ejecutable de Java
    jar_file = "minecraft.jar"  # Cliente del juego
    args = [
        java_path,
        f"-Xmx{ram}M",
        f"-Djava.library.path=natives",
        "-cp", jar_file,
        "net.minecraft.client.main.Main",
        "--username", username,
        "--version", version
    ]
    subprocess.run(args)

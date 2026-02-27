"""
Script para adicionar a variável MINASTAXI_PAYMENT_TYPE no Railway via CLI
"""
import subprocess
import sys

def run_command(cmd, description):
    """Executa comando e mostra resultado"""
    print(f"\n{'='*70}")
    print(f"🔧 {description}")
    print(f"{'='*70}")
    print(f"Comando: {cmd}\n")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print("⚠️ Avisos/Erros:")
            print(result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Erro ao executar comando: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("🚀 CONFIGURAÇÃO DE PAYMENT_TYPE NO RAILWAY")
    print("="*70)
    
    print("\n📋 Este script irá:")
    print("   1. Verificar se Railway CLI está instalado")
    print("   2. Adicionar MINASTAXI_PAYMENT_TYPE=BE")
    print("   3. Verificar a configuração")
    
    # Verificar se Railway CLI está instalado
    print("\n🔍 Verificando Railway CLI...")
    result = subprocess.run("railway --version", shell=True, capture_output=True)
    
    if result.returncode != 0:
        print("\n❌ Railway CLI não está instalado!")
        print("\n📥 Para instalar:")
        print("   npm install -g @railway/cli")
        print("\n   Após instalar, execute este script novamente.")
        sys.exit(1)
    
    print("✅ Railway CLI instalado")
    print(result.stdout.decode())
    
    # Verificar se está logado
    print("\n🔐 Verificando autenticação...")
    result = subprocess.run("railway whoami", shell=True, capture_output=True)
    
    if result.returncode != 0:
        print("\n⚠️ Você precisa fazer login no Railway")
        print("\n🔓 Executando: railway login")
        run_command("railway login", "Login no Railway")
    else:
        print("✅ Já autenticado no Railway")
    
    # Listar variáveis atuais
    print("\n📋 Variáveis atuais no Railway:")
    run_command("railway variables", "Listando variáveis")
    
    # Adicionar variável
    print("\n➕ Adicionando MINASTAXI_PAYMENT_TYPE=BE...")
    
    input("\n⏸️  Pressione ENTER para continuar ou Ctrl+C para cancelar...")
    
    success = run_command(
        "railway variables set MINASTAXI_PAYMENT_TYPE=BE",
        "Configurando forma de pagamento"
    )
    
    if success:
        print("\n✅ Variável adicionada com sucesso!")
        
        # Verificar
        print("\n🔍 Verificando configuração...")
        run_command("railway variables", "Variáveis finais")
        
        print("\n" + "="*70)
        print("✅ CONFIGURAÇÃO CONCLUÍDA!")
        print("="*70)
        print("\n📌 Próximos passos:")
        print("   1. Aguarde o redeploy automático (~2 minutos)")
        print("   2. Verifique os logs: railway logs")
        print("   3. Busque por: 💳 Tipo de pagamento: BE")
        print("\n" + "="*70 + "\n")
    else:
        print("\n❌ Erro ao adicionar variável")
        print("\n🔧 ALTERNATIVA - Adicionar manualmente:")
        print("   1. Acesse: https://railway.app")
        print("   2. Selecione o projeto")
        print("   3. Vá em Variables")
        print("   4. Adicione: MINASTAXI_PAYMENT_TYPE=BE")
        print("   5. Clique em Deploy")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Operação cancelada pelo usuário.")
        sys.exit(0)

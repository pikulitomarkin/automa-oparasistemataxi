"""
Teste de conexão IMAP com o email Hostinger
"""
import os
from dotenv import load_dotenv
from src.services.email_reader import EmailReader

def test_email_connection():
    """Testa conexão com o servidor IMAP e lista emails recentes."""
    
    # Carrega variáveis de ambiente
    load_dotenv(override=True)
    
    print("="*80)
    print("🔍 TESTE DE CONEXÃO - EMAIL IMAP")
    print("="*80)
    print()
    
    # Exibe configuração (sem senha)
    email_host = os.getenv('EMAIL_HOST')
    email_port = os.getenv('EMAIL_PORT')
    email_user = os.getenv('EMAIL_USER')
    email_folder = os.getenv('EMAIL_FOLDER', 'INBOX')
    subject_filter = os.getenv('EMAIL_SUBJECT_FILTER', 'PROGRAMAÇÃO')
    
    print("📧 CONFIGURAÇÃO:")
    print(f"   Host: {email_host}")
    print(f"   Port: {email_port}")
    print(f"   User: {email_user}")
    print(f"   Folder: {email_folder}")
    print(f"   Filter: {subject_filter}")
    print()
    
    try:
        print("🔌 Conectando ao servidor IMAP...")
        
        # Inicializa o EmailReader
        email_reader = EmailReader(
            host=email_host,
            port=int(email_port),
            user=email_user,
            password=os.getenv('EMAIL_PASSWORD'),
            folder=email_folder,
            subject_filter=subject_filter
        )
        
        print("✅ Conexão estabelecida com sucesso!")
        print()
        
        # Busca emails recentes
        print("📬 Buscando emails recentes...")
        emails = email_reader.fetch_new_orders(days_back=30, mark_as_seen=False)
        
        print(f"✅ Total de emails encontrados: {len(emails)}")
        print()
        
        if emails:
            print("="*80)
            print("📨 ÚLTIMOS EMAILS:")
            print("="*80)
            
            for idx, email in enumerate(emails[:5], 1):  # Mostra até 5
                print()
                print(f"Email #{idx}")
                print(f"   De: {email.from_}")
                print(f"   Assunto: {email.subject}")
                print(f"   Data: {email.date}")
                print(f"   Tamanho do corpo: {len(email.body)} caracteres")
                print(f"   Preview: {email.body[:100]}..." if len(email.body) > 100 else f"   Corpo: {email.body}")
                print("-" * 80)
        else:
            print("ℹ️  Nenhum email encontrado com o filtro especificado")
            print(f"   (Buscando assunto contendo: '{subject_filter}')")
        
        print()
        print("="*80)
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("="*80)
        
        return True
        
    except Exception as e:
        print()
        print("="*80)
        print("❌ ERRO NA CONEXÃO")
        print("="*80)
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensagem: {str(e)}")
        print()
        print("💡 POSSÍVEIS CAUSAS:")
        print("   • Credenciais incorretas")
        print("   • Host/porta incorretos")
        print("   • Firewall bloqueando porta 993")
        print("   • IMAP não habilitado na conta")
        print("="*80)
        
        return False

if __name__ == "__main__":
    test_email_connection()

"""
Email reader service using IMAP.
"""
import logging
from typing import List, Optional
from dataclasses import dataclass
from imap_tools import MailBox, AND
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class EmailMessage:
    """Representa um e-mail simplificado."""
    uid: str
    subject: str
    from_: str
    date: datetime
    body: str


class EmailReader:
    """
    Serviço para leitura de e-mails via IMAP.
    Focado em buscar e-mails com assunto específico.
    """
    
    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        folder: str = "INBOX",
        subject_filter: str = "PROGRAMAÇÃO"
    ):
        """
        Inicializa o leitor de e-mails.
        
        Args:
            host: Servidor IMAP (ex: imap.gmail.com).
            port: Porta IMAP (geralmente 993 para SSL).
            user: Usuário/e-mail para login.
            password: Senha ou App Password.
            folder: Pasta a ser monitorada.
            subject_filter: Texto a buscar no assunto (padrão: "PROGRAMAÇÃO" para capturar emails de táxi/carro).
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.folder = folder
        self.subject_filter = subject_filter
        
    def connect(self) -> MailBox:
        """
        Estabelece conexão com o servidor IMAP.
        
        Returns:
            Objeto MailBox conectado.
        """
        try:
            mailbox = MailBox(self.host, self.port)
            mailbox.login(self.user, self.password)
            logger.info(f"Connected to {self.host} as {self.user}")
            return mailbox
        except Exception as e:
            logger.error(f"Failed to connect to email server: {e}")
            raise
    
    def fetch_new_orders(
        self,
        days_back: int = 7,
        mark_as_seen: bool = False
    ) -> List[EmailMessage]:
        """
        Busca e-mails não lidos com o filtro de assunto.
        
        Args:
            days_back: Número de dias para trás na busca.
            mark_as_seen: Se True, marca os e-mails como lidos.
            
        Returns:
            Lista de EmailMessage com os pedidos encontrados.
        """
        messages = []
        
        try:
            with self.connect() as mailbox:
                mailbox.folder.set(self.folder)
                
                # Calcula data de corte
                date_since = datetime.now() - timedelta(days=days_back)
                
                # Busca e-mails não lidos com o assunto específico
                criteria = AND(
                    subject=self.subject_filter,
                    seen=False,
                    date_gte=date_since.date()
                )
                
                for msg in mailbox.fetch(criteria, mark_seen=mark_as_seen):
                    # Extrai o corpo do e-mail (texto plano ou HTML)
                    body = msg.text or msg.html or ""
                    
                    email_msg = EmailMessage(
                        uid=msg.uid,
                        subject=msg.subject,
                        from_=msg.from_,
                        date=msg.date,
                        body=body
                    )
                    
                    messages.append(email_msg)
                    logger.info(
                        f"Fetched email UID={msg.uid}, "
                        f"Subject='{msg.subject}', From={msg.from_}"
                    )
                
                logger.info(f"Total new order emails found: {len(messages)}")
                
        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            raise
        
        return messages
    
    def mark_as_read(self, uid: str):
        """
        Marca um e-mail específico como lido.
        
        Args:
            uid: UID único do e-mail.
        """
        try:
            with self.connect() as mailbox:
                mailbox.folder.set(self.folder)
                mailbox.seen(uid, True)
                logger.info(f"Email UID={uid} marked as read")
        except Exception as e:
            logger.error(f"Error marking email as read: {e}")
    
    def test_connection(self) -> bool:
        """
        Testa a conexão com o servidor IMAP.
        
        Returns:
            True se a conexão foi bem-sucedida.
        """
        try:
            with self.connect() as mailbox:
                folders = list(mailbox.folder.list())
                logger.info(f"Connection successful. Available folders: {folders}")
                return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

📧 MODELO DE EMAIL PARA TESTE COMPLETO DA PLATAFORMA

📮 PARA: agendamento@minastaxi.com.br
🔤 ASSUNTO: PROGRAMAÇÃO (ou PROGRAMAÇÃO DE TAXI)
📅 DATA: Hoje

═══════════════════════════════════════════════════════════

PROGRAMAÇÃO

Data: 30/12/2025
Horário de chegada DELP: 14:30

Passageiros:
1. Ana Silva Rodrigues - +55 31 9999-9926 - Rua Rio de Janeiro, 500, Centro, Belo Horizonte, MG
2. Carlos Eduardo Santos - +55 31 9999-9926 - Avenida Afonso Pena, 1200, Centro, Belo Horizonte, MG
3. Maria Fernanda Costa - +55 31 9999-9926 - Rua da Bahia, 800, Centro, Belo Horizonte, MG
4. João Paulo Oliveira - +55 31 9999-9926 - Praça da Liberdade, 1, Funcionários, Belo Horizonte, MG

Destino: DELP - Delegacia Especializada de Proteção à Criança e ao Adolescente
Endereço destino: Rua Curitiba, 832, Centro, Belo Horizonte, MG

Centro de custo: 1.07002.07.001
Observações: Transporte oficial - Grupo teste plataforma múltiplos passageiros
Solicitante: Sistema Automação MinasTaxi

═══════════════════════════════════════════════════════════

🧪 FUNCIONALIDADES QUE SERÃO TESTADAS:

✅ Múltiplos passageiros (4 pessoas)
✅ Geocoding individual de cada endereço
✅ Otimização de rota por proximidade do destino
✅ Cálculo de horário de saída (14:00 - 30min antes da chegada)
✅ Extração LLM de dados estruturados
✅ Dispatch para API MinasTaxi
✅ Coordenadas individuais para cada passageiro
✅ Database SQLite com persistência
✅ WhatsApp notification (se configurado)

═══════════════════════════════════════════════════════════

📋 RESULTADO ESPERADO:

1. 📧 Sistema detecta email com assunto "PROGRAMAÇÃO" ou "PROGRAMAÇÃO DE TAXI"
2. 🤖 LLM extrai 4 passageiros com endereços individuais
3. 🌍 Geocoding de todos os 5 endereços (4 origem + 1 destino)
4. 🎯 Otimização: Último passageiro mais próximo do DELP
5. 🚕 API MinasTaxi recebe payload com 4 usuários
6. 💾 Order salvo no SQLite com status DISPATCHED
7. 📱 WhatsApp enviado para +55 31 9999-9926

═══════════════════════════════════════════════════════════

🔄 SEQUÊNCIA DE COLETA ESPERADA (após otimização):

O sistema deve organizar a coleta colocando o passageiro mais próximo 
do DELP (Rua Curitiba, Centro) como último a ser coletado.

Ordem provável:
1° → Praça da Liberdade (Funcionários) - mais longe
2° → Avenida Afonso Pena (Centro)
3° → Rua da Bahia (Centro)  
4° → Rua Rio de Janeiro (Centro) - mais próximo do DELP

═══════════════════════════════════════════════════════════

💡 INSTRUÇÕES DE USO:

1. Copie todo o conteúdo entre as linhas ═══
2. Cole em um novo email
3. Configure:
   - PARA: agendamento@minastaxi.com.br
   - ASSUNTO: PROGRAMAÇÃO (ou PROGRAMAÇÃO DE TAXI)
4. Envie o email
5. Aguarde ~5 minutos para processamento
6. Verifique no Dashboard Railway os resultados
7. Confirme no WhatsApp +55 31 9999-9926

═══════════════════════════════════════════════════════════

🚀 ESTE EMAIL TESTA TODAS AS FUNCIONALIDADES IMPLEMENTADAS!

- ✅ Múltiplos passageiros
- ✅ Otimização de rota
- ✅ Geocoding individual  
- ✅ API MinasTaxi
- ✅ Database persistente
- ✅ WhatsApp integration
- ✅ Sistema completo end-to-end

═══════════════════════════════════════════════════════════
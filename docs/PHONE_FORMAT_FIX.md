# 📱 Formatação de Telefone - DDI para MinasTaxi vs WhatsApp

## 🎯 Problema Resolvido

O sistema MinasTaxi **não aceita DDI** no campo de telefone, mas o WhatsApp **precisa do DDI** para envio internacional.

## ✅ Solução Implementada

### Para MinasTaxi API:
- ❌ **Remover DDI (55)**
- ✅ Enviar apenas: **DDD + Número**
- Exemplo: `5531999999926` → `31999999926`

### Para WhatsApp (Evolution API):
- ✅ **Manter DDI (55)**
- ✅ Enviar formato completo: **55 + DDD + Número**
- Exemplo: `31999999926` → `5531999999926`

## 🔧 Código Modificado

### Arquivo: `src/services/minastaxi_client.py`

Adicionada função `_remove_country_code()`:

```python
def _remove_country_code(self, phone: str) -> str:
    """
    Remove DDI (55) do telefone brasileiro para envio ao MinasTaxi.
    
    MinasTaxi espera apenas DDD + número (ex: 31999999926).
    WhatsApp precisa do formato completo com DDI (ex: 5531999999926).
    """
    if not phone:
        return ""
    
    digits_only = ''.join(filter(str.isdigit, phone))
    
    # Se começa com 55 e tem 12-13 dígitos, remove o 55
    if digits_only.startswith('55') and len(digits_only) in [12, 13]:
        return digits_only[2:]
    
    return digits_only
```

### Aplicado em 3 lugares:

1. **Telefone do array `users[]`** (múltiplos passageiros):
   ```python
   "phone": self._remove_country_code(passenger.get('phone', order.phone))
   ```

2. **Telefone do passageiro único**:
   ```python
   "phone": self._remove_country_code(order.phone)
   ```

3. **Campo `passenger_phone_number`** do payload:
   ```python
   "passenger_phone_number": self._remove_country_code(order.phone or ...)
   ```

## ✅ Testes Validados

| Input             | Output MinasTaxi | Output WhatsApp   |
|-------------------|------------------|-------------------|
| `5531999999926`   | `31999999926`    | `5531999999926`   |
| `31999999926`     | `31999999926`    | `5531999999926`   |
| `+5531999999926`  | `31999999926`    | `5531999999926`   |
| `5543988713278`   | `43988713278`    | `5543988713278`   |

## 📋 Arquivo WhatsApp (não modificado)

O arquivo `src/services/whatsapp_notifier.py` já possui a função `normalize_phone()` que **adiciona o DDI** se não estiver presente:

```python
def normalize_phone(self, phone: str) -> str:
    digits_only = re.sub(r'\D', '', phone)
    
    # Se não começar com 55, adiciona
    if not digits_only.startswith('55'):
        digits_only = '55' + digits_only
    
    return digits_only
```

## 🎉 Resultado Final

- ✅ **MinasTaxi** recebe telefones SEM DDI (ex: `31999999926`)
- ✅ **WhatsApp** recebe telefones COM DDI (ex: `5531999999926`)
- ✅ Sistema processa ambos os formatos corretamente
- ✅ Tela do MinasTaxi mostra DDD no lugar certo (não mais DDI ocupando espaço do DDD)

## 🧪 Como Testar

```bash
# Teste a função de formatação
py test_phone_format.py

# Teste envio completo (MinasTaxi + WhatsApp)
py test_sistema_completo.py
```

---

**Status**: ✅ Implementado e testado
**Data**: 30/12/2025

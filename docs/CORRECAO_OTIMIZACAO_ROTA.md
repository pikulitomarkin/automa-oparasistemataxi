# Correção: Otimização de Rota por Distância

## Problema Identificado

Após a implementação da restrição geográfica (bounds de Minas Gerais) no geocoding, o sistema **perdeu a funcionalidade de otimização de rota por distância**.

### Causa Raiz

Quando o geocoding do **endereço de destino** falhava devido às restrições de bounds, a variável `destination_coords` ficava como `None`. Sem as coordenadas do destino, o `RouteOptimizer.optimize_pickup_sequence()` simplesmente retornava os passageiros na ordem original, **sem otimização**.

### Fluxo do Problema

```
1. order.dropoff_address = "Shopping Del Rey, BH"
2. geocode_address() com bounds → FALHA (endereço fora dos bounds ou impreciso)
3. destination_coords = None
4. RouteOptimizer.optimize_pickup_sequence(passengers, None)
5. Retorna passageiros na ordem ORIGINAL (sem otimização)
```

## Solução Implementada

### 1. Novo Método `geocode_address_fallback()`

Adicionado em `src/services/geocoding_service.py`:
- Faz geocoding **SEM restrições de bounds**
- Usado apenas quando o geocoding com bounds falha
- Garante que sempre tenhamos coordenadas de destino para otimização

### 2. Lógica de Fallback no Processor

Modificado em `src/processor.py` (2 locais):

**Processamento Normal (linha ~269):**
```python
# Geocode destino primeiro (CRÍTICO para otimização de rota)
destination_coords = None
if order.dropoff_address:
    dropoff_coords = self.geocoder.geocode_address(order.dropoff_address)
    if dropoff_coords:
        order.dropoff_lat, order.dropoff_lng = dropoff_coords
        destination_coords = dropoff_coords
        logger.info(f"Destination geocoded: {order.dropoff_lat}, {order.dropoff_lng}")
    else:
        # FALLBACK: tentar geocoding sem restrições de bounds
        logger.warning(f"Failed to geocode destination with bounds: {order.dropoff_address}")
        logger.info("Trying fallback geocoding without bounds restrictions...")
        dropoff_coords = self.geocoder.geocode_address_fallback(order.dropoff_address)
        if dropoff_coords:
            order.dropoff_lat, order.dropoff_lng = dropoff_coords
            destination_coords = dropoff_coords
            logger.info(f"Destination geocoded (fallback): {order.dropoff_lat}, {order.dropoff_lng}")
        else:
            logger.error(f"Failed to geocode destination even with fallback: {order.dropoff_address}")
```

**Processamento de Ida e Volta (linha ~491):**
```python
# Geocoding e otimização para IDA
destination_coords = None
if outbound_order.dropoff_address:
    dropoff_coords = self.geocoder.geocode_address(outbound_order.dropoff_address)
    if dropoff_coords:
        outbound_order.dropoff_lat, outbound_order.dropoff_lng = dropoff_coords
        destination_coords = dropoff_coords
    else:
        # FALLBACK: tentar sem restrições para otimização de rota
        logger.warning(f"Failed to geocode outbound destination with bounds")
        dropoff_coords = self.geocoder.geocode_address_fallback(outbound_order.dropoff_address)
        if dropoff_coords:
            outbound_order.dropoff_lat, outbound_order.dropoff_lng = dropoff_coords
            destination_coords = dropoff_coords
            logger.info(f"Outbound destination geocoded (fallback): {dropoff_coords}")
```

## Comportamento Após Correção

### Fluxo Correto

```
1. order.dropoff_address = "Shopping Del Rey, BH"
2. geocode_address() com bounds → FALHA
3. ⚠️  FALLBACK: geocode_address_fallback() sem bounds → SUCESSO
4. destination_coords = (-19.9520, -43.9950) ✓
5. RouteOptimizer.optimize_pickup_sequence(passengers, destination_coords)
6. Retorna passageiros ORDENADOS por distância ✓
```

### Exemplo Real

**Passageiros (ordem original):**
1. João - Centro (7.04 km do destino)
2. Maria - Santo Agostinho (3.50 km do destino)
3. Pedro - São Bento (2.86 km do destino)

**Após otimização:**
1. João (mais longe - embarca PRIMEIRO)
2. Maria (distância média)
3. Pedro (mais próximo - embarca POR ÚLTIMO) ✓

**Lógica:** O passageiro mais próximo do destino embarca por último, minimizando desvios de rota.

## Testes Criados

1. **`test_route_optimization.py`**: Testa otimização básica com coordenadas válidas
2. **`test_fallback_optimization.py`**: Simula falha do geocoding com bounds e valida funcionamento do fallback

## Arquivos Modificados

- `src/services/geocoding_service.py`: Adicionado método `geocode_address_fallback()`
- `src/processor.py`: Adicionada lógica de fallback em 2 locais (processamento normal e ida/volta)

## Resultado

✅ **Otimização de rota por distância restaurada**
✅ **Compatível com restrições de bounds**
✅ **Fallback automático quando necessário**
✅ **Logs informativos para debugging**

---

**Data da Correção:** 06/01/2026
**Autor:** Sistema de Automação de Táxi - IA Assistant

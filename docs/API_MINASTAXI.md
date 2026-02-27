# Documentação API MinasTaxi - Original Software

## Informações Gerais

- **Formato**: JSON
- **Métodos**: POST (preferencial) ou GET
- **Autenticação**: Basic Auth no header
- **URL Base**: `https://vm2c.taxifone.com.br:11048`
- **User (Contrato)**: `02572696000156`
- **Password**: `0104`

## Autenticação

```
Header: authorization: Basic Original.#2024
```

## Códigos de Resposta HTTP

| Código | Significado | Comentário |
|--------|-------------|------------|
| 200 | OK | Resposta padrão para requisições bem-sucedidas |
| 500 | Internal Error | Erro genérico (pode conter estrutura de erro no body) |

---

## 1. getOffer

Solicita o melhor táxi disponível segundo posição do cliente e preferências. Retorna valor estimado da viagem.

### Endpoint
```
POST /getOffer
```

### Request Body
```json
{
  "partner": "322",
  "user": "10222525000108",
  "password": "1059",
  "request_id": "12345678ABC",
  "pickup_time": "1549957900",
  "distance": "2000",
  "duration": "600",
  "stopped_time": "5",
  "pickup": {
    "address": "ALAMEDA OLGA, 422",
    "city": "Sao Paulo",
    "state": "SP",
    "postal_code": "01155-040",
    "lat": "-23.55555",
    "lng": "-46.66666"
  },
  "destination": {
    "address": "AV PAULISTA, 2800",
    "city": "Sao Paulo",
    "state": "SP",
    "postal_code": "01643-000",
    "lat": "-23.65345",
    "lng": "-46.72346"
  }
}
```

**Campos:**
- `partner`: ID do parceiro (string)
- `user`: ID do contrato/empresa (string)
- `password`: Senha de acesso (string)
- `request_id`: ID único da requisição (string)
- `pickup_time`: UNIX Time (segundos desde epoch) (string)
- `distance`: Distância em metros (opcional - pode ser calculado pela API) (string)
- `duration`: Duração estimada em segundos (string)
- `stopped_time`: Tempo parado em minutos (string)
- `pickup`: Objeto com endereço de origem
- `destination`: Objeto com endereço de destino (opcional)

### Response
```json
{
  "request_id": "12345678ABC",
  "success": "True",
  "data": [
    {
      "name": "Regular Taxi",
      "code": "taxi",
      "cost": "21.50",
      "eta": "120",
      "number": "235",
      "lat": "-23.55555",
      "lng": "-46.66666"
    },
    {
      "name": "Taxi Premium",
      "code": "taxi_premium",
      "cost": "23.80",
      "eta": "180",
      "number": "814",
      "lat": "-23.53325",
      "lng": "-46.67656"
    }
  ]
}
```

---

## 2. rideCreate ⭐ (PRINCIPAL)

Solicita agendamento de táxi com todas as informações necessárias.

### Endpoint
```
POST /rideCreate
```

### Request Body
```json
{
  "partner": "322",
  "user": "10222525000108",
  "password": "1059",
  "request_id": "12345678ABC",
  "pickup_time": "1549957900",
  "distance": "2000",
  "stopped_time": "5",
  "category": "taxi",
  "passengers_no": 1,
  "suitcases_no": 1,
  "cost_center": "1.07002.07.004",          # NOVO campo oficial para centro de custo
  "passenger_note": "someNote",
  "passenger_name": "Joao da silva",
  "passenger_phone_number": "11923989655",
  "payment_type": "ONLINE_PAYMENT",        # Tipo de pagamento configurável
  "extra1": "someExtraField1",
  "extra2": "someExtraField2",
  "extra3": "someExtraField3",
  "extra4": "someExtraField4",
  "users": [
    {
      "id": 1,
      "sequence": 1,
      "name": "Passageiro 1",
      "phone": "11992181117",
      "pickup": {
        "address": "ALAMEDA OLGA, 422",
        "neighborhood": "Barra Funda",
        "city": "Sao Paulo",
        "state": "SP",
        "postal_code": "01155-040",
        "reference": "Travessa da Av Pacaembu",
        "lat": "-23.55555",
        "lng": "-46.66666"
      }
    },
    {
      "id": 2,
      "sequence": 3,
      "name": "Passageiro 2",
      "phone": "119922222222",
      "pickup": {
        "address": "RUA TEATRAL, 333",
        "neighborhood": "Pinheiros",
        "city": "Sao Paulo",
        "state": "SP",
        "postal_code": "01155-040",
        "reference": "Pacaembu",
        "lat": "-23.44444",
        "lng": "-46.88888"
      }
    }
  ],
  "destinations": [
    {
      "passengerId": 1,
      "sequence": 2,
      "location": {
        "address": "RUA JABAQUARA, 1200",
        "city": "Sao Paulo",
        "state": "SP",
        "postal_code": "01155-040",
        "reference": "Perto da lua",
        "lat": "-23.99999",
        "lng": "-46.77777"
      }
    },
    {
      "passengerId": 2,
      "sequence": 4,
      "location": {
        "address": "RUA TEATRAL, 333",
        "district": "Pinheiros",
        "city": "Sao Paulo",
        "state": "SP",
        "postal_code": "01155-040",
        "reference": "Pacaembu",
        "lat": "-23.44444",
        "lng": "-46.88888"
      }
    }
  ]
}
```

**Campos Obrigatórios:**
- `partner`: ID do parceiro
- `user`: ID do contrato/empresa
- `password`: Senha de acesso
- `request_id`: ID único da requisição
- `pickup_time`: UNIX Time (segundos desde epoch)
- `category`: Categoria do táxi (ex: "taxi", "taxi_premium")
- `passenger_name`: Nome do passageiro
- `passenger_phone_number`: Telefone do passageiro
- `users`: Array com pelo menos 1 passageiro e seu endereço de origem

**Campos Opcionais:**
- `distance`: Distância em metros (pode ser calculado pela API)
- `stopped_time`: Tempo parado
- `passengers_no`: Número de passageiros (padrão: 1)
- `suitcases_no`: Número de malas (padrão: 0)
- `passenger_note`: Observações
- `payment_type`: Tipo de pagamento
- `cost_center`: Novo campo para centro de custo (substitui a dependência de `extra2`)
- `extra1`, `extra2`, `extra3`, `extra4`: Campos extras customizados (ainda mantidos para compatibilidade)
- `destinations`: Array com destinos (opcional se já informado no user)

### Response
```json
{
  "ride_id": "6365",
  "accepted_and_looking_for_driver": true
}
```

---

## 3. rideCancel

Solicita cancelamento de agendamento e informa o motivo.

### Endpoint
```
POST /rideCancel
```

### Request Body
```json
{
  "partner": "322",
  "user": "10222525000108",
  "password": "1059",
  "request_id": "12345678ABC",
  "ride_id": "12345",
  "cancel_reason": "Any reason"
}
```

### Response
```json
{
  "cancel_accepted": true,
  "cancel_reason": "Any reason"
}
```

---

## 4. rideDetails

Consulta status e posicionamento do táxi de um pedido. 
**Enviado a cada 10 segundos via Web Hook ou pode ser consultado ativamente.**

### Endpoint
```
POST /rideDetails
```

### Request Body
```json
{
  "partner": "322",
  "user": "10222525000108",
  "password": "1059",
  "request_id": "12345678ABC",
  "ride_id": "12345"
}
```

### Response
```json
{
  "request_id": "12345678ABC",
  "user": "12345",
  "password": "5AXCDFG22",
  "ride_id": "6365",
  "taxi_id": "122",
  "taxi_brand": "FIAT",
  "taxi_model": "IDEA",
  "taxi_plate": "ASB-0B33",
  "taxi_lat": "-23.43566",
  "taxi_lng": "-46.63499",
  "driver_name": "ANTONIO DA SILVA",
  "driver_phone": "11996555587",
  "status_code": "ACCEPTED",
  "status_information": "ACCEPTED",
  "message": "I'm waiting outside the building",
  "start_time": "1549957900",
  "finish_time": "1549957922",
  "finish_details": "any obs",
  "finish_address": "Destino efetivo",
  "route_distance": "12.40",
  "price_stopped": "0.00",
  "price_other": "0.00",
  "price_toll": "3.50",
  "price": "23.50",
  "price_estimated": "0.00",
  "price_per_km_b1": "0.00",
  "price_per_km_b2": "0.00",
  "price_on_start": "0.00",
  "price_b1": "0.00",
  "price_b2": "0.00",
  "route_distance_b1": "0.00",
  "route_distance_b2": "0.00",
  "time_stopped_seconds": "0.00",
  "booked_for_later": false,
  "b2": false
}
```

**Status Possíveis:**
- `ACCEPTED`: Pedido aceito
- `DRIVER_EN_ROUTE`: Motorista a caminho
- `AT_PICKUP`: Motorista no local de coleta
- `PASSENGER_ON_BOARD`: Passageiro embarcado
- `CANCELED`: Cancelado
- `COMPLETED`: Corrida finalizada
- `MESSAGE_TO_CUSTOMER`: Mensagem para o cliente

**Observações:**
- Parâmetro `price` disponível apenas no status `COMPLETED`
- Parâmetro `message` disponível no status `MESSAGE_TO_CUSTOMER`

---

## 5. driverDetails

Solicita detalhes do motorista de uma corrida e sua foto.

### Endpoint
```
POST /driverDetails
```

### Request Body
```json
{
  "partner": "322",
  "user": "10222525000108",
  "password": "1059",
  "ride_id": "12345"
}
```

### Response
```json
{
  "success": true,
  "taxi_id": "123",
  "taxi_model": "Renault Logan",
  "driver_name": "Manoel Sampaio",
  "picture": "FDE1233445545665768768789080"
}
```

**Campos:**
- `picture`: Imagem codificada em Base64

---

## 6. driverMessage

Envia mensagem de texto para o motorista.

### Endpoint
```
POST /driverMessage
```

### Request Body
```json
{
  "partner": "322",
  "user": "10222525000108",
  "password": "1059",
  "request_id": "12345678ABC",
  "ride_id": "12345",
  "msg": "teste de envio de mensagem para o motorista"
}
```

### Response
```json
{
  "success": true
}
```

---

## Observações Importantes

1. **Horários**: Sempre em formato UNIX Time (segundos desde epoch)
2. **Coordenadas**: Formato string com ponto decimal (ex: "-23.55555")
3. **Autenticação**: Sempre incluir header `authorization: Basic Original_<credentials>`
4. **IDs únicos**: `request_id` deve ser único para cada requisição
5. **Arrays users/destinations**: Usar campo `sequence` para ordenar paradas múltiplas
6. **Webhook**: Sistema pode enviar `rideDetails` a cada 10 segundos automaticamente

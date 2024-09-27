## QR Code Generator

Este projeto implementa um gerador de códigos QR em Python. O código utiliza a biblioteca `reedsolo` para adição de correção de erro e a biblioteca `PIL` para manipulação de imagens.

### Funcionalidades

- **Geração de Código QR**: Cria códigos QR a partir de dados de entrada, aplicando correção de erro adaptativa.
- **Modo de Codificação**: Utiliza o modo de byte para codificação de dados.
- **Detecção de Erros**: Implementa correção de erro usando códigos de Reed-Solomon.
- **Desenho de Padrões**: Inclui padrões de localização, alinhamento e temporização no código QR.

### Como Usar

1. **Instalação das Dependências**:
   Certifique-se de que as bibliotecas necessárias estejam instaladas:
   ```bash
   pip install reedsolo pillow
   ```

2. **Executar o Código**:
   Basta executar o script Python, onde `qr_data` é a string que você deseja codificar em um código QR.

   ```python
   qr_data = "Hello, QR Code!"
   qr_code_image = create_qr_code(qr_data)
   qr_code_image.show()
   ```

3. **Configurações Opcionais**:
   Você pode ajustar o nível de correção de erro (`L`, `M`, `Q`, `H`), a escala do código QR e a largura da borda ao chamar a função `create_qr_code`.

### Estrutura do Código

- **QR_VERSIONS**: Dicionário que define as capacidades de armazenamento de cada versão do código QR.
- **ERROR_CORRECTION_LEVELS**: Dicionário que relaciona os níveis de correção de erro com seus índices.
- **Funções Principais**:
  - `choose_qr_version`: Escolhe a versão do código QR com base no comprimento dos dados.
  - `generate_qr_code_data_with_error_correction_adaptive`: Gera os dados do código QR, incluindo a correção de erros.
  - `create_qr_code`: Cria a imagem do código QR.

### TO-DO

- **Função de Inserção de Dados no Código QR**: Implementar uma função que insere os dados no QRcode.

### Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir problemas (issues) ou enviar pull requests (PRs).

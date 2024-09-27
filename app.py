from reedsolo import RSCodec
from PIL import Image

QR_VERSIONS = {
    1: {"L": 152, "M": 128, "Q": 104, "H": 72},
    2: {"L": 272, "M": 224, "Q": 176, "H": 128},
    3: {"L": 440, "M": 352, "Q": 272, "H": 208},
    4: {"L": 640, "M": 512, "Q": 368, "H": 272},
    5: {"L": 864, "M": 672, "Q": 496, "H": 368},
    6: {"L": 1080, "M": 816, "Q": 608, "H": 480},
    7: {"L": 1300, "M": 976, "Q": 704, "H": 528},
    8: {"L": 1560, "M": 1240, "Q": 880, "H": 640}
}

ERROR_CORRECTION_LEVELS = {
    'L': 0, 'M': 1, 'Q': 2, 'H': 3
}

ALIGNMENT_PATTERN_LOCATIONS = {
    2: [6, 18],
    3: [6, 22],
    4: [6, 26],
    5: [6, 30],
    6: [6, 34],
    7: [6, 22, 38],
    8: [6, 24, 42],
}

def choose_qr_version(data_length, error_correction_level='M'):
    for version, capacities in QR_VERSIONS.items():
        if data_length <= capacities[error_correction_level]:
            return version
    raise ValueError("Os dados são grandes demais para qualquer versão do QR Code suportar.")

def get_mode_indicator():
    return '0100'

def get_character_count_indicator(data):
    return format(len(data), '08b')

def encode_byte_mode(data):
    binary_data = ''.join(format(ord(c), '08b') for c in data)
    return binary_data

def add_terminator(binary_data, total_bits_required=104):
    terminator_length = min(4, total_bits_required - len(binary_data))
    return binary_data + '0' * terminator_length

def pad_to_multiple_of_8(binary_data):
    while len(binary_data) % 8 != 0:
        binary_data += '0'
    return binary_data

def add_pad_bytes(binary_data, total_bits_required=104):
    pad_bytes = ['11101100', '00010001']
    binary_data = binary_data.replace(' ', '')
    while len(binary_data) < total_bits_required:
        for pad_byte in pad_bytes:
            if len(binary_data) + 8 <= total_bits_required:
                binary_data += pad_byte
            else:
                break
    return binary_data

def add_error_correction(binary_data, total_bytes, error_correction_bytes=7):
    data_bytes = bytearray(int(binary_data[i:i+8], 2) for i in range(0, len(binary_data), 8))
    rsc = RSCodec(error_correction_bytes)
    encoded = rsc.encode(data_bytes)
    correction_bytes = encoded[len(data_bytes):]
    correction_bits = ''.join(format(byte, '08b') for byte in correction_bytes)
    
    return binary_data + correction_bits

def generate_qr_code_data_with_error_correction_adaptive(data, error_correction_level='M'):
    mode_indicator = get_mode_indicator()
    char_count_indicator = get_character_count_indicator(data)
    encoded_data = encode_byte_mode(data)
    total_data_bits = len(mode_indicator + char_count_indicator + encoded_data)
    chosen_version = choose_qr_version(total_data_bits, error_correction_level)
    total_bits_required = QR_VERSIONS[chosen_version][error_correction_level]
    binary_data = mode_indicator + char_count_indicator + encoded_data
    binary_data = add_terminator(binary_data, total_bits_required)
    binary_data = pad_to_multiple_of_8(binary_data)
    binary_data = add_pad_bytes(binary_data, total_bits_required)
    binary_data = add_error_correction(binary_data, total_bits_required // 8, error_correction_bytes=7)
    
    return binary_data, chosen_version

def decode_qr_code_data(binary_data):
    mode_indicator = binary_data[:4]
    if mode_indicator != '0100':
        raise ValueError("O Mode Indicator não corresponde ao Byte Mode (0100).")
    
    character_count_indicator = binary_data[4:12]
    character_count = int(character_count_indicator, 2) 
    data_bits = binary_data[12:12 + (character_count * 8)]
    decoded_data = ''
    for i in range(0, len(data_bits), 8):
        byte = data_bits[i:i+8]
        decoded_data += chr(int(byte, 2))
    return decoded_data

def draw_finder_pattern(pixels, top_left_x, top_left_y, scale):
    """Desenha um padrão de localização no QR Code."""
    for x in range(7):
        for y in range(7):
            if x == 0 or x == 6 or y == 0 or y == 6:
                color = 0 
            elif x == 1 or x == 5 or y == 1 or y == 5: 
                color = 1 
            else:
                color = 0

            for i in range(scale):
                for j in range(scale):
                    pixels[(top_left_x + x) * scale + i, (top_left_y + y) * scale + j] = color

def draw_position_markers(pixels, scale, border, matrix_size):
    marker_size = 7
    positions = [
        (border, border), 
        (border, matrix_size - marker_size + border),
        (matrix_size - marker_size + border, border) 
    ]
    
    for px, py in positions:
        draw_finder_pattern(pixels, px, py, scale)

def draw_alignment_pattern(pixels, scale, border, cx, cy):
    """Desenha um padrão de alinhamento de 5x5 com um quadrado preto no centro."""
    for x in range(-2, 3):
        for y in range(-2, 3):
            px = (cx + x) * scale + border * scale
            py = (cy + y) * scale + border * scale
            color = 0
            if abs(x) == 2 or abs(y) == 2: 
                color = 0
            elif abs(x) == 1 or abs(y) == 1:
                color = 1
            else:
                color = 0
            for i in range(scale):
                for j in range(scale):
                    pixels[px + i, py + j] = color

def draw_alignment_patterns(pixels, scale, border, matrix_size, version):
    """Desenha os padrões de alinhamento baseados na versão do QR code."""
    if version < 2:
        return 
    
    positions = ALIGNMENT_PATTERN_LOCATIONS.get(version, [])
    for cx in positions:
        for cy in positions:
            if not ((cx <= 7 and cy <= 7) or (cx <= 7 and cy >= matrix_size - 8) or 
                    (cx >= matrix_size - 8 and cy <= 7)):
                draw_alignment_pattern(pixels, scale, border, cx, cy)

def draw_timing_pattern(pixels, scale, border, matrix_size):
    for x in range(6, matrix_size - 6):
        bit = (x % 2 == 0)
        for i in range(scale):
            for j in range(scale):
                pixels[(border + 6) * scale + i, (border + x) * scale + j] = 0 if bit else 1

    for y in range(6, matrix_size - 6):
        bit = (y % 2 == 0)
        for i in range(scale):
            for j in range(scale):
                pixels[(border + y) * scale + i, (border + 6) * scale + j] = 0 if bit else 1
     
def create_qr_code(data, scale=10, border=4, error_correction_level='L'):
    binary_data, version = generate_qr_code_data_with_error_correction_adaptive(data, error_correction_level)
    matrix_size = 21 + (version - 1) * 4 
    image_size = (matrix_size + border * 2) * scale 
    image = Image.new("1", (image_size, image_size), 1) 
    pixels = image.load()
    
    draw_position_markers(pixels, scale, border, matrix_size)
    draw_alignment_patterns(pixels, scale, border, matrix_size, version)
    draw_timing_pattern(pixels, scale, border, matrix_size)
    return image

qr_data = "Hello, QR Code!"
qr_code_image = create_qr_code(qr_data)
qr_code_image.show()
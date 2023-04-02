import tensorflow as tf
import os

# 파라미터 준비
DN_FILTERS = 256 # 컨볼루셔널 레이어 커널 수
DN_RESIDUAL_NUM = 19 # 레지듀얼 블록 수
DN_INPUT_SHAPE = (15, 15, 3) # 입력 형태
DN_OUTPUT_SIZE = 225 # 행동 수

# 컨볼루셔널 레이어 생성
def conv(filters):
    return tf.keras.layers.Conv2D(filters, 3, padding = 'same', use_bias = False, kernel_initializer = 'he_normal', kernel_regularizer = tf.keras.regularizers.l2(0.0005))

# 레지듀얼 블록 생성(ResNet)
def residual_block():
    def f(x):
        sc = x
        x = conv(DN_FILTERS)(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Activation('relu')(x)
        x = conv(DN_FILTERS)(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Add()([x, sc])
        x = tf.keras.layers.Activation('relu')(x)
        
        return x
    
    return f

# 듀얼 네트워크 생성
def dual_network():
    # 모델 생성이 완료된 경우 처리하지 않음
    if os.path.exists('./model/best.h5'):
        return
    
    # 입력 레이어
    input = tf.keras.layers.Input(shape = DN_INPUT_SHAPE)

    # 컨볼루셔널 레이어
    x = conv(DN_FILTERS)(input)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Activation('relu')(x)

    # 레지듀얼 블록 × 19
    for _ in range(DN_RESIDUAL_NUM):
        x = residual_block()(x)

    # 풀링 레이어
    x = tf.keras.layers.GlobalAveragePooling2D()(x)

    # 정책 출력
    p = tf.keras.layers.Dense(DN_OUTPUT_SIZE, kernel_regularizer = tf.keras.regularizers.l2(0.0005), activation = 'softmax', name = 'pi')(x)

    # 가치 출력
    v = tf.keras.layers.Dense(1, kernel_regularizer = tf.keras.regularizers.l2(0.0005))(x)
    v = tf.keras.layers.Activation('tanh', name = 'v')(v)

    # 모델 생성
    model = tf.keras.Model(inputs = input, outputs = [p, v])

    # 모델 저장
    os.makedirs('./model/', exist_ok = True) # 폴더가 없는 경우 생성
    model.save('./model/best.h5') # 베스트 플레이어 모델

    # 모델 삭제
    tf.keras.backend.clear_session()
    del model

if __name__ == '__main__':
    dual_network()
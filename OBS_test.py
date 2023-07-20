# OBS Studio Python Scriptingの初期化
import obspython as obs

# スクリプトの開始時に実行される関数
def script_load(settings):
    # スクリプトがロードされたときに実行したい初期化コードをここに書く
    pass

# シーンを切り替える関数
def switch_scene(scene_name):
    current_scene = obs.obs_frontend_get_current_scene()
    scene = obs.obs_get_scene_by_name(scene_name)
    if scene and current_scene != scene:
        obs.obs_frontend_set_current_scene(scene)

# スクリプトの停止時に実行される関数
def script_unload():
    # スクリプトがアンロードされたときに実行したいクリーンアップコードをここに書く
    pass

# シーン切り替えボタンが押されたときに実行される関数
def switch_scene_button_clicked(props, prop):
    scene_name = obs.obs_data_get_string(props, "scene_name")
    # scene_name = obs.obs_data_get_string(obs.obs_properties_get(props, "シーン2"))
    switch_scene(scene_name)

# スクリプトがアクティブになったときに実行される関数
def script_description():
    return "シーンを切り替えるカスタムスクリプト"

# GUI（グラフィカルユーザーインターフェース）の設定
def script_properties():
    props = obs.obs_properties_create()

    # ボタンを作成
    obs.obs_properties_add_button(props, "button", "シーン切り替えe", switch_scene_button_clicked)

    # テキスト入力を作成
    obs.obs_properties_add_text(props, "scene_name", "切り替えるシーン名", obs.OBS_TEXT_DEFAULT)

    return props

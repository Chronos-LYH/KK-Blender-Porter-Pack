translation_dictionary = {

    'seams'     : "体を縫合する",
    'seams_tt'  : '体に近い頂点をマージ。 このマージには首のウエイトが台無しになる可能性がある（テクスチャアトラスが台無しになる可能性もある）。 このオプションを無効にしたらウエイトが保存されるけど体に縫い目が見えるかも',
    
    'outline'     : '一つのアウトラインモード',
    'outline_tt'  : "このオプションにしたらシングルのアウトラインを使われる。 このオプションにしたらアウトライン透明の問題が起こるかも",
    
    'keep_templates'        : "マテリアルテンプレートを保存",
    'keep_templates_tt'     : "KKBPマテリアルテンプレートをフェイクユーザーに設定する",

    'sfw_mode'          : 'エロ無しモード',
    'sfw_mode_tt'       : 'プラグインがエロの部分を隠してみる',

    'arm_drop'          :"アーマチュアのタイプ",
    'arm_drop_A'        : "KKBPアーマチュアにする",
    'arm_drop_A_tt'     : "KKBPアーマチュアにする。この設定にはアーマチュアは改造されて、ベーシックなIKがジェネレートされる",
    'arm_drop_B'        : "Rigifyアーマチュアにする",
    'arm_drop_B_tt'     : "Rigifyアーマチュアにする。この設定にはBlenderでの使用アーマチュアがジェネレートされる",
    'arm_drop_C'        : "コイカツのアーマチュアにする",
    'arm_drop_C_tt'     : "コイカツのアーマチュアにする。この設定にはボーンの名前、アーマチュアの構造はコイカツのアーマチュアと一致される",
    'arm_drop_D'        : "PMXアーマチュアにする",
    'arm_drop_D_tt'     : "PMXアーマチュアにする。この設定にはアーマチュアが改造されない",

    'cat_drop'      : '操作タイプ',
    'cat_drop_A'    : "別々にしない",
    'cat_drop_A_tt' : "すべてをインポートして一つの服オブジェクトにする。別の服はひとりでに隠される",
    'cat_drop_C'    : "すべてを別々にする",
    'cat_drop_C_tt' : "すべてをインポートして個々の服オブジェクトにする",
    'cat_drop_D'    : "SMRデータでカテゴライズ",
    'cat_drop_D_tt' : "すべてをインポートしてSMR(Skinned Mesh Renderer)データで服を別々にする。この設定にはマテリアルテンプレートや色データや使われないからモデルはテクスチャーなしで見える",

    'dark'      : "ダークな色",
    'dark_C'    : "ダークな色は変更しない",
    'dark_C_tt' : "ダークな色はライトな色と同じにする",
    'dark_F'    : 'AUTO',
    'dark_F_tt' : "実験的なスクリプトでダークな色をセットする",

    'prep_drop'         : "エクスポートタイプ",
    'prep_drop_A'       : "Unity - VRMコンパチ",
    'prep_drop_A_tt'    : """アウトラインを削除して...
    Eyewhiteの複写を削除して,
    Unityがボーンをひとりでに見つけられるためにアーマチュアを改造して""",
    'prep_drop_B'       : "汎用FBX - 変更なし",
    'prep_drop_B_tt'    : """アウトラインを削除して...
    Eyewhiteの複写を削除して""",
    'prep_drop_D'       : "Unity - VRChatコンパチ",
    'prep_drop_D_tt'    : """アウトラインを削除して...
    Eyewhiteの複写を削除して,
    Upper Chestの骨を削除して、
    Unityがボーンをひとりでに見つけられるためにアーマチュアを改造して""",

    'simp_drop'     : 'アーマチュアの簡略化',
    'simp_drop_A'   : '超シンプル (遅い)',
    'simp_drop_A_tt': 'この設定には骨の数が減る。瞳の骨をアーマチュアレイヤー１に移って, アーマチュアレイヤー3,4,5,11,12,17,18,19の骨が簡略化される (約100骨が残る)',
    'simp_drop_B'   : 'シンプル',
    'simp_drop_B_tt': 'この設定には骨の数が減る。瞳の骨をアーマチュアレイヤー１に移って, アーマチュアレイヤー11の骨が簡略化される (約500骨が残る)',
    'simp_drop_C'   : '簡略化してない (早い)',
    'simp_drop_C_tt': 'アーマチュアが簡略化されない',
    
    'bake'          : 'マテリアルテンプレートをファイナライズ',
    'bake_light'    : "ライト",
    'bake_light_tt' : "ライトテクスチャーをファイナライズ",
    'bake_dark'     : "ダーク",
    'bake_dark_tt'  : "ダークテクスチャーをファイナライズ",
    'bake_norm'     : "ノーマル",
    'bake_norm_tt'  : "ノーマルテクスチャーをファイナライズ",
    'bake_mult'     : 'ファイナライズ乗数',
    'bake_mult_tt'  : "ファイナライズしたテクスチャーがぼやけている場合は２，３にしてみて",
    'old_bake'      : 'V4ベーカー',
    'old_bake_tt'   : 'ふるいテクスチャーベーカーを使う。V4ベーカーはUVMap2,3,4をファイナライズできないから髪のハイライトや目のアイシャドウをファイナライズされない',

    'shape_A'       : 'KKBPシェイプキーにする',
    'shape_A_tt'    : 'シェイプキーを変更して部分的なシェイプキーを削除する',
    'shape_B'       : "部分的なシェイプキーを保存",
    'shape_B_tt'    : "シェイプキーを変更して部分的なシェイプキーを保存する",
    'shape_C'       : "シェイプキー変更しない",
    'shape_C_tt'    : "コイカツのシェイプキーにする。シェイプキーが変更されない",

    'shader_A'       : 'Eeveeにする',
    'shader_B'       : "Cyclesにする",
    'shader_C'       : "Eevee modにする",
    'shader_C_tt'    : "別のEeveeシェーダー設定にする", 

    'import_export' : 'インポート ・ エクスポート',
    'extras'        : '追加機能',
    'import_model'  : 'モデルをインポート',
    'prep'          : 'ターゲットアプリのために準備する',

    'studio_object'             : 'スタジオオブジェクトをインポート',
    'studio_object_tt'          : 'SB3Utilityでエクスポートされた.fbxファイルのフォルダを読み取る',
    'convert_texture'           : 'テクスチャを和度する?',
    'convert_texture_tt'        : '''このオプションにしたら、コイカツのLUTでテクスチャの色を和度される''',
    'single_animation'          : '一つのアニメーションファイルをインポート',
    'single_animation_tt'       : 'Rigifyアーマチュアが必要です。SB3UtilityでエクスポートしたFBXのアニメーションファイルをチャラのアーマチュアにインポートする。MixamoのFBXアニメーションファイルもインポートできる（下のトグルをクリックして）',
    'animation_koi'             : 'コイカツアニメーションをインポート',
    'animation_mix'             : 'Mixamoアニメーションをインポート',
    'animation_type_tt'         : 'コイカツの.fbxアニメーションをインポートする場合はこの設定を無効にして。Mixamoの.fbxアニメーションをインポートする場合はこの設定を有効にして。',
    'animation_library'         : 'Rigifyアーマチュアが必要です。アニメーションライブラリをジェネレートする',
    'animation_library_tt'      : "現行ファイルとキャラクタでアニメーションライブラリをジェネレートする。SB3UtilityでエクスポートしたFBXファイルのフォルダを選択して",
    'animation_library_scale'   : '腕をスケール',
    'animation_library_scale_tt': 'このオプションにしたら腕のYスケールを5%で掛けられる。（ポースの精度は高める）',
    'map_library'               : 'マップアセットライブラリをジェネレートする',
    'map_library_tt'            : "現行ファイルでマップアセットライブラリをジェネレートする。SB3UtilityでエクスポートしたFBXファイルのフォルダを選択して。マップ一つにつき500秒まで掛かれる",

    'rigify_convert'            : "Rigifyアーマチュアに変えて",
    'rigify_convert_tt'         : "このボタンをクリックしたら、KKBPアーマチュアをRigifyアーマチュアに変えて",
    'sep_eye'                   : "EyesやEyebrowsやBodyのオブジェクトから別々になって",
    # 'sep_eye_tt'                : "Separates the Eyes and Eyebrows from the Body object and links the shapekeys to the Body object. Useful for when you want to make eyes or eyebrows appear through the hair using the Cryptomatte features in the compositor",
    'bone_visibility'           : "現在の服のボーンを表示して",
    'bone_visibility_tt'        : "このボタンをクリックしたら、不要なアクセサリボーンをビューポートで隠くされる。たとえば、Outfit 00 と Outfit 01 ビューポートで隠されない場合は、すべてのアクセサリボーンが表示される。Outfit 00 をビューポートで隠してこのボタンをクリックすると、Outfit 01 のアクセサリボーンのみが表示されます。",
    # 'export_sep_meshes'         : "Export Seperate Meshes",
    # 'export_sep_meshes_tt'      : "Only available for the \"Separate by SMR data\" option. Choose where to export meshes",

    'kkbp_import_tt'            : "コイカツモデル(.PMXフォーマット)をインポートして改造して",
    'export_prep_tt'            : "KKBPアーマチュアが必要です。メニューの情報をチェックして",
    'bake_mats_tt'              : "マテリアルテンプレートをPNGファイルにする。PNGファイルはPMXフォルダーに保存される",

    'delete_cache' : 'キャッシュを削除する',
    'delete_cache_tt' : """このオプションにしたらキャッシュファイルを削除される。
モデルをインポートされるときに、マテリアルをファイナライズされるときに、キャッシュファイルが生成される。
キャッシュファイルはＰＭＸフォルダーに「atlas_files」、「baked_files」、「dark_files」、「saturated_files」フォルダーに保存される。 
このオプションにしたら、それらのフォルダーのすべてのファイルを削除される""",

    'use_atlas' : 'アトラスを生成する',
    'use_atlas_tt': '時間を節約したい場合は、アトラスの生成をしないことができる',
    'dont_use_atlas' : 'アトラスを生成しない',

    'mat_comb_tt' : 'KKBPは Shotariya の Material Combiner アドオンの一部を使用して、マテリアルをアトラスに自動的に結合します。KKBPにマテリアルを結合させるのではなく、手動でマテリアルを結合したい場合は、このボタンをクリックして (Material Combiner アドオンをダウンロードする必要があります。そして、KKBP パネルの [マテリアルテンプレートをファイナライズ] ボタンを既にクリックしていることを確認してください。クリックしていないと機能しません)',
    'matcomb' : 'Material Combinerの手動準備',
    'pillow' : 'アトラス機能を使用するにはPILをインストール',
    'pillow_tt':'Pillow をインストールするにはクリックして。インストールはしばらく時間がかかる。',
    'reset_mats' : 'ファイナライズしたマテリアルをリセット',
    'reset_mats_tt' : 'このボタンをクリックしたら、すべてのファイナライズしたマテリアルが -ORG バージョンにリセットされます。すべてを再ファイナライズしたい場合に便利です。',

    }


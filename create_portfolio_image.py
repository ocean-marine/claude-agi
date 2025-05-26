#!/usr/bin/env python3
"""
ポートフォリオ画像作成スクリプト
imagesディレクトリ内のJPGファイルをパッチワーク風に配置して
一つの大きなPNGファイルを作成します。
"""

import os
import math
from PIL import Image, ImageOps
import glob

def create_portfolio_image():
    """メイン処理: JPGファイルをパッチワーク風に配置したPNGを作成"""
    
    # 画像ディレクトリのパス
    images_dir = "images"
    
    # JPGファイルを取得
    jpg_files = glob.glob(os.path.join(images_dir, "*.jpg"))
    jpg_files.sort()  # ファイル名でソート
    
    if not jpg_files:
        print("JPGファイルが見つかりませんでした。")
        return
    
    print(f"{len(jpg_files)}個のJPGファイルを発見しました。")
    
    # 標準サイズを設定（最も多いサイズに合わせる）
    standard_width = 400  # 元の画像の半分のサイズに
    standard_height = 266  # アスペクト比を維持
    
    # グリッドサイズを計算（正方形に近い配置）
    num_images = len(jpg_files)
    grid_cols = math.ceil(math.sqrt(num_images))
    grid_rows = math.ceil(num_images / grid_cols)
    
    print(f"グリッドサイズ: {grid_cols} x {grid_rows}")
    
    # キャンバスサイズを計算
    canvas_width = grid_cols * standard_width
    canvas_height = grid_rows * standard_height
    
    print(f"最終画像サイズ: {canvas_width} x {canvas_height}")
    
    # 白いキャンバスを作成
    canvas = Image.new('RGB', (canvas_width, canvas_height), 'white')
    
    # 各画像を配置
    for i, jpg_file in enumerate(jpg_files):
        try:
            # 画像を開く
            img = Image.open(jpg_file)
            
            # アスペクト比を維持してリサイズ
            img = ImageOps.fit(img, (standard_width, standard_height), Image.Resampling.LANCZOS)
            
            # グリッド位置を計算
            col = i % grid_cols
            row = i // grid_cols
            
            # 配置位置を計算
            x = col * standard_width
            y = row * standard_height
            
            # キャンバスに貼り付け
            canvas.paste(img, (x, y))
            
            print(f"配置完了: {os.path.basename(jpg_file)} -> ({x}, {y})")
            
        except Exception as e:
            print(f"エラー: {jpg_file} の処理中にエラーが発生しました: {e}")
            continue
    
    # PNGとして保存
    output_file = "portfolio_image.png"
    canvas.save(output_file, "PNG", quality=95)
    
    print(f"\nポートフォリオ画像が作成されました: {output_file}")
    print(f"最終サイズ: {canvas_width} x {canvas_height}")

def main():
    """エントリーポイント"""
    try:
        create_portfolio_image()
    except ImportError:
        print("エラー: Pillowライブラリが必要です。")
        print("以下のコマンドでインストールしてください:")
        print("pip install Pillow")
    except Exception as e:
        print(f"予期しないエラーが発生しました: {e}")

if __name__ == "__main__":
    main()
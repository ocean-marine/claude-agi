#!/usr/bin/env python3
"""
ポートフォリオ画像作成スクリプト
imagesディレクトリ内のJPGファイルをパッチワーク風に配置して
一つの大きなPNGファイルを作成します。
アスペクト比が混在する画像に対応しています。
"""

import os
import math
from PIL import Image, ImageOps
import glob

def analyze_images(jpg_files):
    """画像を分析してアスペクト比に基づいてグループ化"""
    landscape_images = []
    portrait_images = []
    square_images = []
    
    for jpg_file in jpg_files:
        try:
            with Image.open(jpg_file) as img:
                width, height = img.size
                aspect_ratio = width / height
                
                if aspect_ratio > 1.2:  # 横長
                    landscape_images.append(jpg_file)
                elif aspect_ratio < 0.8:  # 縦長
                    portrait_images.append(jpg_file)
                else:  # 正方形に近い
                    square_images.append(jpg_file)
                    
        except Exception as e:
            print(f"エラー: {jpg_file} の分析中にエラーが発生しました: {e}")
            continue
    
    return landscape_images, portrait_images, square_images

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
    
    # 画像をアスペクト比で分類
    landscape_images, portrait_images, square_images = analyze_images(jpg_files)
    
    print(f"横長画像: {len(landscape_images)}枚")
    print(f"縦長画像: {len(portrait_images)}枚")
    print(f"正方形画像: {len(square_images)}枚")
    
    # 標準セルサイズを設定（最大公約数的なサイズ）
    cell_width = 400
    cell_height = 300
    
    # グリッドサイズを計算（正方形に近い配置）
    num_images = len(jpg_files)
    grid_cols = math.ceil(math.sqrt(num_images))
    grid_rows = math.ceil(num_images / grid_cols)
    
    print(f"グリッドサイズ: {grid_cols} x {grid_rows}")
    
    # キャンバスサイズを計算
    canvas_width = grid_cols * cell_width
    canvas_height = grid_rows * cell_height
    
    print(f"最終画像サイズ: {canvas_width} x {canvas_height}")
    
    # 白いキャンバスを作成
    canvas = Image.new('RGB', (canvas_width, canvas_height), 'white')
    
    # すべての画像を混在して配置（自然な感じに）
    all_images = jpg_files  # 元の順序を保持
    
    # 各画像を配置
    for i, jpg_file in enumerate(all_images):
        try:
            # 画像を開く
            img = Image.open(jpg_file)
            original_width, original_height = img.size
            
            # アスペクト比を計算
            aspect_ratio = original_width / original_height
            
            # セルサイズに基づいてターゲットサイズを決定
            if aspect_ratio > 1.5:  # 非常に横長の場合
                target_width = cell_width
                target_height = int(cell_width / aspect_ratio)
                # セル内で上下中央配置用のオフセット
                y_offset = (cell_height - target_height) // 2
                x_offset = 0
            elif aspect_ratio < 0.7:  # 非常に縦長の場合
                target_height = cell_height
                target_width = int(cell_height * aspect_ratio)
                # セル内で左右中央配置用のオフセット
                x_offset = (cell_width - target_width) // 2
                y_offset = 0
            else:  # 通常のアスペクト比
                # セル全体を使用してフィット
                img = ImageOps.fit(img, (cell_width, cell_height), Image.Resampling.LANCZOS)
                target_width = cell_width
                target_height = cell_height
                x_offset = 0
                y_offset = 0
            
            # 通常のアスペクト比以外の場合はリサイズ
            if aspect_ratio > 1.5 or aspect_ratio < 0.7:
                img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            
            # グリッド位置を計算
            col = i % grid_cols
            row = i // grid_cols
            
            # 配置位置を計算（オフセットを考慮）
            x = col * cell_width + x_offset
            y = row * cell_height + y_offset
            
            # キャンバスに貼り付け
            canvas.paste(img, (x, y))
            
            print(f"配置完了: {os.path.basename(jpg_file)} -> ({x}, {y}) [{target_width}x{target_height}]")
            
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
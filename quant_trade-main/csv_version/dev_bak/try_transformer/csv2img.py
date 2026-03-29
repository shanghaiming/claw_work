import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
import os
import numpy as np
from tqdm import tqdm
import glob
from PIL import Image

class MultiCSVKLineGenerator:
    def __init__(self, data_folder):
        """
        初始化多CSV文件K线图生成器
        
        参数:
            data_folder: 包含CSV文件的文件夹路径
        """
        self.data_folder = data_folder
        self.csv_files = self._find_csv_files()
        
    def _find_csv_files(self):
        """查找指定文件夹中的所有CSV文件"""
        csv_pattern = os.path.join(self.data_folder, "*.csv")
        csv_files = glob.glob(csv_pattern)
        
        if not csv_files:
            raise ValueError(f"在文件夹 {self.data_folder} 中未找到CSV文件")
            
        print(f"找到 {len(csv_files)} 个CSV文件")
        return csv_files
    
    def _load_and_preprocess_data(self, csv_file):
        """加载并预处理单个CSV数据"""
        df = pd.read_csv(csv_file)
        
        # 检查必要的列是否存在
        required_columns = ['trade_date', 'open', 'high', 'low', 'close', 'volume']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"CSV文件 {csv_file} 中缺少必要的列: {col}")
        
        # 将日期列转换为datetime类型并设置为索引
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        df.set_index('trade_date', inplace=True)
        
        # 确保数据按日期排序
        df.sort_index(inplace=True)
        
        return df
    
    def generate_rolling_charts_for_all(self, output_base_folder='kline_images', 
                                       window_size=100, step=5, style='charles'):
        """
        为所有CSV文件生成滚动窗口K线图（包含成交量）
        
        参数:
            output_base_folder: 输出图片的基础文件夹
            window_size: 每个窗口包含的数据点数量
            step: 窗口移动的步长（天数）
            style: 图表样式
            
        返回:
            所有生成的图片路径列表
        """
        all_image_paths = []
        
        for csv_file in self.csv_files:
            try:
                # 获取股票名称用于文件名和文件夹
                stock_name = os.path.splitext(os.path.basename(csv_file))[0]
                output_folder = os.path.join(output_base_folder, stock_name)
                
                # 创建输出文件夹
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
                
                print(f"\n处理文件: {stock_name}")
                
                # 加载数据
                df = self._load_and_preprocess_data(csv_file)
                
                # 生成滚动窗口图表
                image_paths = self._generate_rolling_charts_for_file(
                    df, stock_name, output_folder, window_size, step, style
                )
                
                all_image_paths.extend(image_paths)
                
            except Exception as e:
                print(f"处理文件 {csv_file} 时出错: {e}")
                continue
        
        print(f"\n完成! 共生成 {len(all_image_paths)} 张K线图")
        return all_image_paths
    
    def _generate_rolling_charts_for_file(self, df, stock_name, output_folder, 
                                         window_size, step, style):
        """为单个CSV文件生成滚动窗口K线图（包含成交量）"""
        image_paths = []
        total_points = len(df)
        
        # 计算需要生成的图表数量
        num_windows = (total_points - window_size) // step + 1
        print(f"将生成 {num_windows} 张K线图，每张图包含 {window_size} 个数据点")
        
        # 检查是否有所需的均线列
        ma_columns = ['ma5', 'ma8', 'ma13']
        has_ma = all(col in df.columns for col in ma_columns)
        
        if not has_ma:
            print("警告: CSV文件中缺少均线列，将只绘制K线图和成交量")
        
        # 使用进度条显示生成进度
        for start_idx in tqdm(range(0, total_points - window_size + 1, step), 
                             desc=f"生成 {stock_name} 的K线图"):
            end_idx = start_idx + window_size
            window_data = df.iloc[start_idx:end_idx]
            
            # 创建文件名
            start_date = window_data.index[0].strftime('%Y%m%d')
            end_date = window_data.index[-1].strftime('%Y%m%d')
            output_path = os.path.join(output_folder, f"{stock_name}_{start_date}_{end_date}.png")
            
            # 检查文件是否已存在，如果存在则跳过
            if os.path.exists(output_path):
                image_paths.append(output_path)
                continue
            
            # 准备均线数据 (如果存在)
            apds = []
            if has_ma:
                # 创建均线绘图对象
                colors = ['orange', 'purple', 'brown']
                for i, ma_col in enumerate(ma_columns):
                    apd = mpf.make_addplot(
                        window_data[ma_col], 
                        color=colors[i], 
                        width=1.5,  # 增加均线宽度以提高可见性
                        panel=0,
                        label=ma_col.upper()
                    )
                    apds.append(apd)
            
            # 创建K线图 - 包含成交量
            try:
                # 设置图表样式
                mc = mpf.make_marketcolors(
                    up='red', down='green',
                    wick={'up': 'red', 'down': 'green'},
                    volume={'up': 'red', 'down': 'green'},
                    edge={'up': 'red', 'down': 'green'},
                    ohlc={'up': 'red', 'down': 'green'}
                )
                s = mpf.make_mpf_style(
                    marketcolors=mc, 
                    gridstyle=':', 
                    y_on_right=True,
                    rc={
                        'lines.linewidth': 1.5,  # 增加线条宽度
                        'lines.markersize': 6,   # 增加标记大小
                        'font.size': 10          # 增加字体大小（虽然不显示，但影响内部元素）
                    }
                )
                
                # 使用兼容的绘图参数
                plot_kwargs = {
                    'type': 'candle',
                    'style': s,
                    'title': '',  # 移除标题
                    'ylabel': '',  # 移除Y轴标签
                    'xlabel': '',  # 移除X轴标签
                    'volume': True,  # 包含成交量
                    'figratio': (10, 8),  # 调整比例以容纳成交量
                    'figscale': 1.2,      # 增加整体比例以提高清晰度
                    'returnfig': True,    # 返回fig对象以便后续处理
                    'axisoff': True,      # 移除坐标轴
                    'scale_padding': {'left': 0, 'right': 0, 'top': 0, 'bottom': 0},
                    'panel_ratios': (4, 1),  # 主图与成交量的高度比例
                }
                
                # 添加均线数据（如果存在）
                if apds:
                    plot_kwargs['addplot'] = apds
                
                # 绘制图表
                fig, axes = mpf.plot(window_data, **plot_kwargs)
                
                # 移除成交量图的坐标轴
                if len(axes) > 1:
                    axes[1].axis('off')
                
                # 提高DPI以获得更清晰的图像
                fig.savefig(output_path, dpi=150, bbox_inches='tight', pad_inches=0)
                plt.close(fig)  # 关闭图形以节省内存
                
                # 使用高质量设置重新保存图像
                img = Image.open(output_path)
                # 保持原始尺寸但使用更高质量保存
                img.save(output_path, optimize=True, quality=100)
                
                image_paths.append(output_path)
                
            except Exception as e:
                print(f"生成 {start_date} 到 {end_date} 图表时出错: {e}")
        
        return image_paths
    
    def create_dataset_summary(self, image_paths, output_csv='dataset_summary.csv'):
        """
        创建数据集摘要CSV文件，包含每张图片对应的股票、日期范围和标签信息
        
        参数:
            image_paths: 生成的图片路径列表
            output_csv: 输出CSV文件路径
        """
        summary_data = []
        
        for img_path in image_paths:
            # 从文件路径提取信息
            path_parts = img_path.split(os.sep)
            stock_name = path_parts[-2]  # 假设路径结构: base_folder/stock_name/图片文件
            filename = path_parts[-1]
            
            # 从文件名提取日期范围
            date_parts = filename.replace('.png', '').split('_')
            start_date = date_parts[-2]
            end_date = date_parts[-1]
            
            # 尝试找到对应的CSV文件
            csv_file = next((f for f in self.csv_files if stock_name in f), None)
            
            if csv_file:
                try:
                    df = self._load_and_preprocess_data(csv_file)
                    
                    # 计算价格变化百分比 (作为示例标签)
                    start_price = df.loc[pd.to_datetime(start_date), 'close']
                    end_price = df.loc[pd.to_datetime(end_date), 'close']
                    price_change = (end_price - start_price) / start_price * 100
                    
                    # 简单分类: 上涨/下跌/持平
                    if price_change > 2:
                        label = "上涨"
                    elif price_change < -2:
                        label = "下跌"
                    else:
                        label = "持平"
                        
                    # 检查是否有均线数据
                    has_ma = all(col in df.columns for col in ['ma5', 'ma8', 'ma13'])
                    
                except:
                    price_change = None
                    label = "未知"
                    has_ma = False
            else:
                price_change = None
                label = "未知"
                has_ma = False
            
            summary_data.append({
                'stock': stock_name,
                'image_path': img_path,
                'start_date': start_date,
                'end_date': end_date,
                'price_change_percent': price_change,
                'label': label,
                'has_moving_averages': has_ma
            })
        
        # 创建DataFrame并保存为CSV
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv(output_csv, index=False)
        print(f"数据集摘要已保存至: {output_csv}")
        
        return summary_df

# 使用示例
if __name__ == "__main__":
    # 替换为包含CSV文件的文件夹路径
    data_folder = fr"E:\stock\backtest\data\analyzed\5min"
    
    # 初始化生成器
    generator = MultiCSVKLineGenerator(data_folder)
    
    # 为所有CSV文件生成滚动窗口K线图（包含成交量）
    image_paths = generator.generate_rolling_charts_for_all(
        output_base_folder=fr"E:\stock\backtest\image",
        window_size=100,
        step=5
    )
    
    # 创建数据集摘要
    summary_df = generator.create_dataset_summary(image_paths, 'kline_dataset_summary_all.csv')
    
    # 显示统计信息
    print("\n数据集统计信息:")
    print(f"股票数量: {summary_df['stock'].nunique()}")
    print(f"图片总数: {len(summary_df)}")
    print(f"标签分布:\n{summary_df['label'].value_counts()}")
    
    # 显示示例图片 (可选)
    if len(image_paths) > 0:
        # 随机选择几张图片显示
        sample_paths = np.random.choice(image_paths, min(4, len(image_paths)), replace=False)
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        axes = axes.flatten()
        
        for i, img_path in enumerate(sample_paths):
            try:
                img = plt.imread(img_path)
                axes[i].imshow(img)
                axes[i].set_title(os.path.basename(img_path))
                axes[i].axis('off')
            except:
                axes[i].text(0.5, 0.5, '无法加载图片', ha='center', va='center')
                axes[i].axis('off')
        
        plt.tight_layout()
        plt.show()
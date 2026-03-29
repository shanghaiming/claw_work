window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        sync_charts: function(relayoutData, ids) {
            console.log("=== sync_charts 开始执行 ===");
            console.log("图表数量:", relayoutData.length);
            
            // 检查是否有有效的触发数据
            const validRelayouts = relayoutData.filter(data => 
                data && (data['xaxis.range[0]'] !== undefined || data['xaxis.autorange'] !== undefined)
            );
            
            if (validRelayouts.length === 0) {
                console.log("没有有效的触发数据，返回 null 数组");
                return Array(relayoutData.length).fill(null);
            }
            
            // 使用第一个有效的触发数据
            const triggeredData = validRelayouts[0];
            console.log("使用触发数据:", triggeredData);
            
            // 同步所有图表
            const syncedData = relayoutData.map((currentData, index) => {
                // 如果是触发源图表，保持原数据不变
                if (currentData && 
                    ((currentData['xaxis.range[0]'] === triggeredData['xaxis.range[0]'] && 
                      currentData['xaxis.range[1]'] === triggeredData['xaxis.range[1]']) ||
                     currentData['xaxis.autorange'] === triggeredData['xaxis.autorange'])) {
                    return currentData;
                }
                
                // 对其他图表应用同步
                if (triggeredData['xaxis.range[0]'] && triggeredData['xaxis.range[1]']) {
                    return {
                        'xaxis.range[0]': triggeredData['xaxis.range[0]'],
                        'xaxis.range[1]': triggeredData['xaxis.range[1]'],
                        'xaxis.autorange': triggeredData['xaxis.autorange'] || false
                    };
                } else if (triggeredData['xaxis.autorange']) {
                    return {
                        'xaxis.autorange': triggeredData['xaxis.autorange']
                    };
                }
                
                return null;
            });
            
            console.log("返回同步结果:", syncedData);
            return syncedData;
        }
    }
});
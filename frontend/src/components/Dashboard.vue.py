< template >
< div


class ="dashboard" >

< h1 > 学生压力数据可视化 < / h1 >

< div


class ="chart-grid" >

< StressChart
:cities = "stress1Cities"
:counts = "stress1Counts"
title = "学业压力最低为1的前6个城市"
/ >

< StressChart
:cities = "stress5Cities"
:counts = "stress5Counts"
title = "学业压力最高为5的前6个城市"
/ >

< !-- 可以继续添加更多图表 -->
< / div >
< / div >
< / template >

< script >
import StressChart
from

'@/components/StressChart.vue';
import

{ref, onMounted}
from

'vue';
import axios
from

'axios';

export
default
{
    components: {StressChart},
    setup() {
        const stress1Cities = ref([]);
const
stress1Counts = ref([]);
const
stress5Cities = ref([]);
const
stress5Counts = ref([]);

const
fetchData = async () = > {
try {
// 获取压力为1的数据
const res1 = await axios.get('/api/stress/1');
stress1Cities.value = res1.data.cities;
stress1Counts.value = res1.data.counts;

// 获取压力为5的数据
const res5 = await axios.get('/api/stress/5');
stress5Cities.value = res5.data.cities;
stress5Counts.value = res5.data.counts;
} catch (error) {
console.error('获取数据失败:', error);
}
};

onMounted(() = > {
    fetchData();
});

return {
    stress1Cities,
    stress1Counts,
    stress5Cities,
    stress5Counts
};
}
};
< / script >

    < style
scoped >
.dashboard
{
    padding: 20px;
background - color:  # f5f7fa;
min - height: 100
vh;
}

.chart - grid
{
    display: grid;
grid - template - columns: repeat(auto - fit, minmax(450
px, 1
fr));
gap: 20
px;
margin - top: 20
px;
}

h1
{
    text - align: center;
color:  # 333;
margin - bottom: 30
px;
}
< / style >
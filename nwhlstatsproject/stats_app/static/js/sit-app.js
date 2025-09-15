const ShotPlot = {
    props: ['points', 'title'],
    template: '<canvas ref="canvas" width="215" height="288"></canvas>',
    data() {
        return {
            chart: null,
            rinkImage: null,
        };
    },
    mounted() {
        this.loadImageAndRender();
    },
    methods: {
        loadImageAndRender() {
            const img = new Image();
            img.src = '/static/images/iihf-rink-half.png';
            img.onload = () => {
                this.rinkImage = img;
                this.renderChart();
            };
        },
        renderChart() {
            const canvas = this.$refs.canvas;
            const context = canvas.getContext('2d');
            
            this.chart = new Chart(context, {
                type: 'scatter',
                data: {
                    datasets: [{
                        label: 'Shot Locations',
                        data: this.points,
                        backgroundColor: 'rgba(255, 0, 0, 0.84)',
                    }]
                },
                options: {
                    animation: false,
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            display: false,
                            min: 125,
                            max: 202
                        },
                        y: {
                            display: false,
                            min: -2,
                            max: 87
                        }
                    },
                    plugins: {
                        title: {
                            display: true,
                            text: this.title,
                            font: {
                                size: 20,
                                weight: 'bold'
                            },
                            color: '#000',
                            padding: {
                                top: 10,
                                bottom: 10
                            }
                        },
                        legend: {
                            display: false
                        },
                        backgroundImage: true
                    }
                },
                plugins: [{
                    id: 'backgroundImage',
                    beforeDraw: (chart) => {
                        const ctx = chart.ctx;
                        const {top, left, width, height} = chart.chartArea;
                        ctx.save();
                        ctx.globalAlpha = 0.2;
                        ctx.drawImage(this.rinkImage, left, top, width, height);
                        ctx.restore();
                    }
                }]
            });
        },
        updateChart() {
            if (this.chart) {
                this.chart.destroy();
            }
            this.renderChart();
        }
    },
    beforeUnmount() {
        if (this.chart) {
            this.chart.destroy();
        }
    },
    watch: {
        points() {
            this.updateChart();
            // handler() {
            //     this.updateChart();
            // },
            // deep: true
        }
    },
};

const appInstance = () => {
    const app = Vue.createApp({
        // change the delimiters since django uses {{}}
        delimiters: ['[[', ']]'],
        data() {
            return {
                loading: true,
                teamDataOne: [],
                teamDataTwo: [],
                teamDataThree: [],
                plotDataOne: [],
                plotDataTwo: [],
                plotDataThree: [],
                currTeamId: 4,
                currTeamLogo: '/static/images/usa_logo.png',
            }
        },
        mounted() {
            // get the team data
            this.getTableData();
            this.getPlotData();
        },
        computed: {
            shotsOne() {
                if (!Array.isArray(this.plotDataOne)) return [];
                return this.plotDataOne.map(data => ({
                    x: data.x_coord,
                    y: data.y_coord
                }));
            },
            shotsTwo() {
                if (!Array.isArray(this.plotDataTwo)) return [];
                return this.plotDataTwo.map(data => ({
                    x: data.x_coord,
                    y: data.y_coord
                }));
            },
            shotsThree() {
                if (!Array.isArray(this.plotDataThree)) return [];
                return this.plotDataThree.map(data => ({
                    x: data.x_coord,
                    y: data.y_coord
                }));
            },
        },
        methods: {
            getTableData() {
                this.loading = true;
                // get period 1 team data
                axios.get('/api/teams/period/', {
                    params: {
                        teamid: this.currTeamId,
                        period: 1,
                        state: '5v5',
                    }
                }).then(response => {
                    this.teamDataOne = response.data[0];
                }).catch(error => {
                    console.log(error)
                });

                // get period 2 team data
                axios.get('/api/teams/period/', {
                    params: {
                        teamid: this.currTeamId,
                        period: 2,
                        state: '5v5',
                    }
                }).then(response => {
                    this.teamDataTwo = response.data[0];
                }).catch(error => {
                    console.log(error)
                });
                
                // get period 3 team data
                axios.get('/api/teams/period/', {
                    params: {
                        teamid: this.currTeamId,
                        period: 3,
                        state: '5v5',
                    }
                }).then(response => {
                    this.teamDataThree = response.data[0];
                }).catch(error => {
                    console.log(error)
                });
                // data has now been loaded
                this.loading = false;
            },
            getPlotData() {
                this.loading = true;
                // get period 1 plot data
                axios.get('/api/shots/period/', {
                    params: {
                        teamid: this.currTeamId,
                        period: 1,
                        state: '5v5',
                    }
                }).then(response => {
                    this.plotDataOne = response.data;
                }).catch(error => {
                    console.log(error)
                });

                // get period 2 team data
                axios.get('/api/shots/period/', {
                    params: {
                        teamid: this.currTeamId,
                        period: 2,
                        state: '5v5',
                    }
                }).then(response => {
                    this.plotDataTwo = response.data;
                }).catch(error => {
                    console.log(error)
                });
                
                // get period 3 team data
                axios.get('/api/shots/period/', {
                    params: {
                        teamid: this.currTeamId,
                        period: 3,
                        state: '5v5',
                    }
                }).then(response => {
                    this.plotDataThree = response.data;
                }).catch(error => {
                    console.log(error)
                });
                // data has now been loaded
                this.loading = false;
            },
            getTeamLogo() {
                this.loading = true;
                if (this.currTeamId == 1) {
                    this.currTeamLogo = '/static/images/ca_logo.png';
                } else if (this.currTeamId == 2) {
                    this.currTeamLogo = '/static/images/fin_logo.png';
                } else if (this.currTeamId == 3) {
                    this.currTeamLogo = '/static/images/rus_logo.png';
                } else {
                    this.currTeamLogo = '/static/images/usa_logo.png';
                }
                this.loading = false;
            },
        },
        watch: {
            // when currTeamId changes, get new data
            currTeamId(newId) {
                this.getTableData();
                this.getTeamLogo();
                this.getPlotData();
            },
        }
    });

    app.component('shotplot', ShotPlot);
    return app;
};

// mount instance to html
appInstance().mount('#sit-tool');
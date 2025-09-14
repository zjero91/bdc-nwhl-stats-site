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
                teamDownTwo: [],
                teamDownOne: [],
                teamEven: [],
                teamUpOne: [],
                teamUpTwo: [],
                plotDownTwo: [],
                plotDownOne: [],
                plotEven: [],
                plotUpOne: [],
                plotUpTwo: [],
                currTeamId: 1,
                currTeamLogo: '/static/images/pride_logo.png',
            }
        },
        mounted() {
            // get the team data
            this.getTableData();
            this.getPlotData();
        },
        computed: {
            shotsDownTwo() {
                if (!Array.isArray(this.plotDownTwo)) return [];
                return this.plotDownTwo.map(data => ({
                    x: data.x_coord,
                    y: data.y_coord
                }));
            },
            shotsDownOne() {
                if (!Array.isArray(this.plotDownOne)) return [];
                return this.plotDownOne.map(data => ({
                    x: data.x_coord,
                    y: data.y_coord
                }));
            },
            shotsEven() {
                if (!Array.isArray(this.plotEven)) return [];
                return this.plotEven.map(data => ({
                    x: data.x_coord,
                    y: data.y_coord
                }));
            },
            shotsUpOne() {
                if (!Array.isArray(this.plotUpOne)) return [];
                return this.plotUpOne.map(data => ({
                    x: data.x_coord,
                    y: data.y_coord
                }));
            },
            shotsUpTwo() {
                if (!Array.isArray(this.plotUpTwo)) return [];
                return this.plotUpTwo.map(data => ({
                    x: data.x_coord,
                    y: data.y_coord
                }));
            },
        },
        methods: {
            getTableData() {
                this.loading = true;
                // get diff -2 team data
                axios.get('/api/teams/goaldiff/', {
                    params: {
                        teamid: this.currTeamId,
                        goaldiff: -2,
                        state: '5v5',
                    }
                }).then(response => {
                    this.teamDownTwo = response.data[0];
                }).catch(error => {
                    console.log(error)
                });

                // get diff -1 team data
                axios.get('/api/teams/goaldiff/', {
                    params: {
                        teamid: this.currTeamId,
                        goaldiff: -1,
                        state: '5v5',
                    }
                }).then(response => {
                    this.teamDownOne = response.data[0];
                }).catch(error => {
                    console.log(error)
                });
                
                // get diff 0 team data
                axios.get('/api/teams/goaldiff/', {
                    params: {
                        teamid: this.currTeamId,
                        goaldiff: 0,
                        state: '5v5',
                    }
                }).then(response => {
                    this.teamEven = response.data[0];
                }).catch(error => {
                    console.log(error)
                });

                // get diff +1 team data
                axios.get('/api/teams/goaldiff/', {
                    params: {
                        teamid: this.currTeamId,
                        goaldiff: 1,
                        state: '5v5',
                    }
                }).then(response => {
                    this.teamUpOne = response.data[0];
                }).catch(error => {
                    console.log(error)
                });

                // get diff +2 team data
                axios.get('/api/teams/goaldiff/', {
                    params: {
                        teamid: this.currTeamId,
                        goaldiff: 2,
                        state: '5v5',
                    }
                }).then(response => {
                    this.teamUpTwo = response.data[0];
                }).catch(error => {
                    console.log(error)
                });

                // data has now been loaded
                this.loading = false;
            },
            getPlotData() {
                this.loading = true;
                // get diff -2 plot data
                axios.get('/api/shots/goaldiff/', {
                    params: {
                        teamid: this.currTeamId,
                        goaldiff: -2,
                        state: '5v5',
                    }
                }).then(response => {
                    this.plotDownTwo = response.data;
                }).catch(error => {
                    console.log(error)
                });

                // get diff -1 team data
                axios.get('/api/shots/goaldiff/', {
                    params: {
                        teamid: this.currTeamId,
                        goaldiff: -1,
                        state: '5v5',
                    }
                }).then(response => {
                    this.plotDownOne = response.data;
                }).catch(error => {
                    console.log(error)
                });
                
                // get diff 0 team data
                axios.get('/api/shots/goaldiff/', {
                    params: {
                        teamid: this.currTeamId,
                        goaldiff: 0,
                        state: '5v5',
                    }
                }).then(response => {
                    this.plotEven = response.data;
                }).catch(error => {
                    console.log(error)
                });

                // get diff +1 team data
                axios.get('/api/shots/goaldiff/', {
                    params: {
                        teamid: this.currTeamId,
                        goaldiff: 0,
                        state: '5v5',
                    }
                }).then(response => {
                    this.plotUpOne = response.data;
                }).catch(error => {
                    console.log(error)
                });

                // get diff +2 team data
                axios.get('/api/shots/goaldiff/', {
                    params: {
                        teamid: this.currTeamId,
                        goaldiff: 2,
                        state: '5v5',
                    }
                }).then(response => {
                    this.plotUpTwo = response.data;
                }).catch(error => {
                    console.log(error)
                });

                // data has now been loaded
                this.loading = false;
            },
            getTeamLogo() {
                this.loading = true;
                if (this.currTeamId == 1) {
                    this.currTeamLogo = '/static/images/pride_logo.png';
                } else if (this.currTeamId == 2) {
                    this.currTeamLogo = '/static/images/beauts_logo.png';
                } else if (this.currTeamId == 3) {
                    this.currTeamLogo = '/static/images/whale_logo.png';
                } else if (this.currTeamId == 4) {
                    this.currTeamLogo = '/static/images/riveters_logo.png';
                } else if (this.currTeamId == 5) {
                    this.currTeamLogo = '/static/images/whitecaps_logo.png';
                } else {
                    this.currTeamLogo = '/static/images/six_logo.png';
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
appInstance().mount('#stats-tool');
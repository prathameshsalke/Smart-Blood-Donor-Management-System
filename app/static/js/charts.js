/**
 * Charts and data visualization for admin dashboard
 */

class ChartManager {
    constructor() {
        this.charts = {};
        this.init();
    }
    
    init() {
        this.initBloodTypeChart();
        this.initDonationTrendChart();
        this.initRequestStatusChart();
        this.initEmergencyChart();
        this.initGeographicChart();
    }
    
    initBloodTypeChart() {
        const ctx = document.getElementById('bloodTypeChart');
        if (!ctx) return;
        
        const bloodTypeData = JSON.parse(ctx.dataset.bloodTypes || '{}');
        
        this.charts.bloodType = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(bloodTypeData),
                datasets: [{
                    data: Object.values(bloodTypeData),
                    backgroundColor: [
                        '#dc3545', '#ff6b6b', '#28a745', '#20c997',
                        '#17a2b8', '#6610f2', '#fd7e14', '#e83e8c'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value} donors (${percentage}%)`;
                            }
                        }
                    }
                },
                cutout: '60%'
            }
        });
    }
    
    initDonationTrendChart() {
        const ctx = document.getElementById('donationTrendChart');
        if (!ctx) return;
        
        const months = JSON.parse(ctx.dataset.months || '[]');
        const donations = JSON.parse(ctx.dataset.donations || '[]');
        
        this.charts.donationTrend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: months,
                datasets: [{
                    label: 'Donations',
                    data: donations,
                    borderColor: '#dc3545',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    borderWidth: 3,
                    pointBackgroundColor: '#dc3545',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    tension: 0.3,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        titleFont: {
                            size: 14
                        },
                        bodyFont: {
                            size: 13
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0,0,0,0.05)'
                        },
                        ticks: {
                            stepSize: 10
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }
    
    initRequestStatusChart() {
        const ctx = document.getElementById('requestStatusChart');
        if (!ctx) return;
        
        const statusData = JSON.parse(ctx.dataset.status || '{}');
        
        this.charts.requestStatus = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Pending', 'Fulfilled', 'Cancelled', 'Expired'],
                datasets: [{
                    label: 'Requests',
                    data: [
                        statusData.pending || 0,
                        statusData.fulfilled || 0,
                        statusData.cancelled || 0,
                        statusData.expired || 0
                    ],
                    backgroundColor: [
                        '#ffc107',
                        '#28a745',
                        '#6c757d',
                        '#dc3545'
                    ],
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0,0,0,0.05)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }
    
    initEmergencyChart() {
        const ctx = document.getElementById('emergencyChart');
        if (!ctx) return;
        
        const emergencyData = JSON.parse(ctx.dataset.emergency || '[]');
        const times = JSON.parse(ctx.dataset.times || '[]');
        
        this.charts.emergency = new Chart(ctx, {
            type: 'line',
            data: {
                labels: times,
                datasets: [{
                    label: 'Emergency Requests',
                    data: emergencyData,
                    borderColor: '#dc3545',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    borderWidth: 2,
                    pointBackgroundColor: '#dc3545',
                    pointBorderColor: '#fff',
                    pointRadius: 4,
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0,0,0,0.05)'
                        }
                    }
                }
            }
        });
    }
    
    initGeographicChart() {
        const ctx = document.getElementById('geographicChart');
        if (!ctx) return;
        
        const cities = JSON.parse(ctx.dataset.cities || '[]');
        const counts = JSON.parse(ctx.dataset.counts || '[]');
        
        this.charts.geographic = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: cities,
                datasets: [{
                    label: 'Donors by City',
                    data: counts,
                    backgroundColor: '#17a2b8',
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: 'rgba(0,0,0,0.05)'
                        }
                    },
                    y: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }
    
    updateCharts(data) {
        // Update blood type chart
        if (this.charts.bloodType && data.bloodTypes) {
            this.charts.bloodType.data.datasets[0].data = Object.values(data.bloodTypes);
            this.charts.bloodType.update();
        }
        
        // Update donation trend
        if (this.charts.donationTrend && data.donations) {
            this.charts.donationTrend.data.datasets[0].data = data.donations;
            this.charts.donationTrend.update();
        }
        
        // Update request status
        if (this.charts.requestStatus && data.requests) {
            this.charts.requestStatus.data.datasets[0].data = [
                data.requests.pending || 0,
                data.requests.fulfilled || 0,
                data.requests.cancelled || 0,
                data.requests.expired || 0
            ];
            this.charts.requestStatus.update();
        }
    }
    
    downloadChartAsImage(chartId) {
        const canvas = document.getElementById(chartId);
        if (!canvas) return;
        
        const link = document.createElement('a');
        link.download = `${chartId}-${new Date().toISOString().split('T')[0]}.png`;
        link.href = canvas.toDataURL('image/png');
        link.click();
    }
    
    exportChartData(chartId) {
        const chart = this.charts[chartId];
        if (!chart) return;
        
        const data = {
            labels: chart.data.labels,
            datasets: chart.data.datasets.map(ds => ({
                label: ds.label,
                data: ds.data
            }))
        };
        
        const jsonStr = JSON.stringify(data, null, 2);
        const blob = new Blob([jsonStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.download = `${chartId}-data.json`;
        link.href = url;
        link.click();
        
        URL.revokeObjectURL(url);
    }
}

// Initialize chart manager
document.addEventListener('DOMContentLoaded', () => {
    window.chartManager = new ChartManager();
});
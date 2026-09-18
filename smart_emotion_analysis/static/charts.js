/**
 * Chart.js Integration for AI YouTube Comment Intelligence
 * Responsive, beautiful, and theme-adaptive (Light & Dark modes)
 */

window.AppCharts = {
    instances: {},

    isDarkMode() {
        return document.documentElement.getAttribute('data-theme') === 'dark';
    },

    getThemeColors() {
        const dark = this.isDarkMode();
        return {
            textColor: dark ? '#cbd5e1' : '#475569',
            gridColor: dark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)',
            tooltipBg: dark ? '#1e293b' : '#0f172a',
            tooltipText: '#ffffff'
        };
    },

    // 1. Sentiment Distribution Donut Chart
    initSentimentDonut(canvasId, positivePct, neutralPct, negativePct) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        if (this.instances[canvasId]) {
            this.instances[canvasId].destroy();
        }

        const theme = this.getThemeColors();

        this.instances[canvasId] = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Positive', 'Neutral', 'Negative'],
                datasets: [{
                    data: [positivePct, neutralPct, negativePct],
                    backgroundColor: [
                        '#10b981', // Emerald
                        '#94a3b8', // Slate
                        '#ef4444'  // Rose
                    ],
                    borderWidth: 2,
                    borderColor: this.isDarkMode() ? '#131d2f' : '#ffffff',
                    hoverOffset: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '72%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: theme.textColor,
                            boxWidth: 12,
                            padding: 16,
                            font: { size: 12, family: 'Inter, sans-serif', weight: '500' }
                        }
                    },
                    tooltip: {
                        backgroundColor: theme.tooltipBg,
                        titleColor: theme.tooltipText,
                        bodyColor: theme.tooltipText,
                        padding: 10,
                        cornerRadius: 8,
                        callbacks: {
                            label: function (context) {
                                return ` ${context.label}: ${context.raw}%`;
                            }
                        }
                    }
                }
            }
        });
    },

    // 2. Sentiment Volume Bar Chart
    initSentimentVolume(canvasId, posCount, neuCount, negCount) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        if (this.instances[canvasId]) {
            this.instances[canvasId].destroy();
        }

        const theme = this.getThemeColors();

        this.instances[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Positive', 'Neutral', 'Negative'],
                datasets: [{
                    label: 'Comments',
                    data: [posCount, neuCount, negCount],
                    backgroundColor: [
                        'rgba(16, 185, 129, 0.85)',
                        'rgba(148, 163, 184, 0.85)',
                        'rgba(239, 68, 68, 0.85)'
                    ],
                    borderRadius: 6,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: theme.tooltipBg,
                        titleColor: theme.tooltipText,
                        bodyColor: theme.tooltipText,
                        padding: 10,
                        cornerRadius: 8
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { color: theme.textColor }
                    },
                    y: {
                        grid: { color: theme.gridColor },
                        ticks: { color: theme.textColor, precision: 0 }
                    }
                }
            }
        });
    },

    // 3. Horizontal Emotion Bar Chart
    initEmotionBars(canvasId, emotionTotals) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        if (this.instances[canvasId]) {
            this.instances[canvasId].destroy();
        }

        const theme = this.getThemeColors();
        const emotions = ['happiness', 'surprise', 'neutral', 'sadness', 'fear', 'anger'];
        const labels = ['Happiness', 'Surprise', 'Neutral', 'Sadness', 'Fear', 'Anger'];
        const values = emotions.map(e => (emotionTotals && emotionTotals[e]) || 0);

        const colors = [
            '#f59e0b', // Happiness (Gold)
            '#8b5cf6', // Surprise (Purple)
            '#64748b', // Neutral (Slate)
            '#3b82f6', // Sadness (Blue)
            '#ec4899', // Fear (Pink/Amber)
            '#ef4444'  // Anger (Red)
        ];

        this.instances[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: colors,
                    borderRadius: 6,
                    borderSkipped: false
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: theme.tooltipBg,
                        titleColor: theme.tooltipText,
                        bodyColor: theme.tooltipText,
                        padding: 10,
                        cornerRadius: 8,
                        callbacks: {
                            label: function (ctx) {
                                return ` Score: ${ctx.raw}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { color: theme.gridColor },
                        ticks: { color: theme.textColor, precision: 0 }
                    },
                    y: {
                        grid: { display: false },
                        ticks: { color: theme.textColor, font: { weight: '600' } }
                    }
                }
            }
        });
    },

    // Update all charts upon Dark/Light mode toggle
    updateTheme() {
        const theme = this.getThemeColors();
        for (const [id, chart] of Object.entries(this.instances)) {
            if (chart.options.scales) {
                if (chart.options.scales.x) {
                    if (chart.options.scales.x.ticks) chart.options.scales.x.ticks.color = theme.textColor;
                    if (chart.options.scales.x.grid && chart.options.scales.x.grid.color) chart.options.scales.x.grid.color = theme.gridColor;
                }
                if (chart.options.scales.y) {
                    if (chart.options.scales.y.ticks) chart.options.scales.y.ticks.color = theme.textColor;
                    if (chart.options.scales.y.grid && chart.options.scales.y.grid.color) chart.options.scales.y.grid.color = theme.gridColor;
                }
            }
            if (chart.options.plugins && chart.options.plugins.legend && chart.options.plugins.legend.labels) {
                chart.options.plugins.legend.labels.color = theme.textColor;
            }
            chart.update();
        }
    }
};

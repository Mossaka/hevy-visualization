// Main JavaScript file for Hevy Analytics

// Category emojis and colors
const categoryEmojis = {
    'Chest': '💪',
    'Back': '🏋️',
    'Legs': '🦵',
    'Shoulders': '🤸',
    'Arms': '💪',
    'Core': '🔥',
    'Other': '⚡'
};

// Color palettes for charts with gradients
const categoryColors = {
    'Chest': '#0ea5e9',
    'Back': '#8b5cf6',
    'Legs': '#ef4444',
    'Shoulders': '#f59e0b',
    'Arms': '#10b981',
    'Core': '#6366f1',
    'Other': '#6b7280'
};

// Gradient colors for enhanced visual appeal
const categoryGradients = {
    'Chest': ['#0ea5e9', '#0284c7'],
    'Back': ['#8b5cf6', '#7c3aed'],
    'Legs': ['#ef4444', '#dc2626'],
    'Shoulders': ['#f59e0b', '#d97706'],
    'Arms': ['#10b981', '#059669'],
    'Core': ['#6366f1', '#4f46e5'],
    'Other': ['#6b7280', '#4b5563']
};

const chartColors = [
    '#0ea5e9', '#8b5cf6', '#ef4444', '#f59e0b', 
    '#10b981', '#6366f1', '#ec4899', '#14b8a6', 
    '#f97316', '#8b5cf6', '#06b6d4', '#84cc16'
];

// Enhanced chart colors with gradients
const enhancedChartColors = [
    '#0ea5e9', '#8b5cf6', '#ef4444', '#f59e0b', 
    '#10b981', '#6366f1', '#ec4899', '#14b8a6', 
    '#f97316', '#a855f7', '#06b6d4', '#84cc16',
    '#f43f5e', '#22d3ee', '#facc15', '#fb7185'
];

// Global variables for month navigation
let availableMonths = [];
let currentMonthIndex = 0;

// Global variables for workout date navigation
let availableWorkoutDates = [];
let currentDateIndex = 0;
let currentDaysCount = 3;

// Cache for recent workouts data
let allWorkoutsData = null;

// Format numbers with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Format minutes to hours and minutes
function formatDuration(minutes) {
    const hours = Math.floor(minutes / 60);
    const mins = Math.round(minutes % 60);
    
    if (hours > 0) {
        return `${hours}h ${mins}m`;
    } else {
        return `${mins}m`;
    }
}

// Initialize the dashboard
document.addEventListener('DOMContentLoaded', function() {
    // Load workout dates for navigation
    loadWorkoutDates();
    
    // Load recent workouts data
    loadRecentWorkouts();
    
    // Load summary data
    loadSummaryData();
    
    // Load time analysis data to get available months
    loadTimeAnalysis();
    
    // Load monthly summary data
    loadMonthlySummary();
    
    // Load Big Three Lifts data
    loadBigThreeAnalysis();
    
    // Load exercise data
    loadExerciseData();
    
    // Load category data
    loadCategoryData();
    
    // Load workout balance data
    loadWorkoutBalanceData();
    
    // Load personal records data
    loadPersonalRecords();
    
    // Load goal setting data
    loadGoalSetting();
    
    // Set up event listeners
    setupEventListeners();
});

// Load summary data
function loadSummaryData() {
    fetch('./data_json/summary.json')
        .then(response => response.json())
        .then(data => {
            // Update summary cards
            document.getElementById('total-exercises').textContent = data.total_exercises;
            document.getElementById('total-sets').textContent = formatNumber(data.total_sets);
            document.getElementById('total-volume').textContent = formatNumber(Math.round(data.total_volume));
            
            // Populate exercise select dropdown
            const exerciseSelect = document.getElementById('exercise-select');
            data.top_exercises.forEach(item => {
                const option = document.createElement('option');
                option.value = item.exercise;
                option.textContent = item.exercise;
                exerciseSelect.appendChild(option);
            });
        })
        .catch(error => console.error('Error loading summary data:', error));
}

// Load monthly summary data
function loadMonthlySummary(month = null) {
    fetch('./data_json/monthly_summary.json')
        .then(response => response.json())
        .then(allMonthsData => {
            // Filter client-side
            let data;
            if (month) {
                data = allMonthsData.find(m => m.month === month);
            } else {
                // Get most recent month
                data = allMonthsData[allMonthsData.length - 1];
            }

            if (!data) {
                console.error('No data found for month:', month);
                return;
            }

            // Update monthly summary title and display
            document.getElementById('monthly-summary-title').textContent = `Performance for ${data.month}`;
            document.getElementById('current-month-display').textContent = data.month;

            // Update monthly summary cards
            document.getElementById('monthly-sets').textContent = formatNumber(data.sets);
            document.getElementById('monthly-volume').textContent = formatNumber(Math.round(data.volume));
            document.getElementById('monthly-duration').textContent = formatDuration(data.duration_minutes);

            // Create monthly top exercises chart
            createMonthlyTopExercisesChart(data.top_exercises);
        })
        .catch(error => console.error('Error loading monthly summary data:', error));
}

// Load time analysis data
function loadTimeAnalysis() {
    fetch('./data_json/time_analysis.json')
        .then(response => response.json())
        .then(data => {
            // Store available months for navigation
            availableMonths = data.monthly.map(item => item.month);
            currentMonthIndex = availableMonths.length - 1; // Start with most recent month
            
            // Update month navigation buttons
            updateMonthNavigationState();
            
            // Create monthly charts
            createMonthlyVolumeChart(data.monthly);
            createMonthlySetsChart(data.monthly);
            createMonthlyDurationChart(data.monthly);
            
            // Create yearly analysis chart
            createYearlyAnalysisChart(data.yearly);
        })
        .catch(error => console.error('Error loading time analysis data:', error));
}

// Load big three analysis data
function loadBigThreeAnalysis() {
    fetch('./data_json/big_three_analysis.json')
        .then(response => response.json())
        .then(data => {
            console.log("Big Three data:", data);  // Debug log
            
            // Update bench press stats
            document.getElementById('bench-max-weight').textContent = data.bench_press.stats.max_weight > 0 ? 
                data.bench_press.stats.max_weight.toFixed(1) + ' lbs' : 'No data';
            document.getElementById('bench-sets').textContent = data.bench_press.stats.sets > 0 ?
                data.bench_press.stats.sets : 'No data';
            
            // Update squat stats
            document.getElementById('squat-max-weight').textContent = data.squat.stats.max_weight > 0 ?
                data.squat.stats.max_weight.toFixed(1) + ' lbs' : 'No data';
            document.getElementById('squat-sets').textContent = data.squat.stats.sets > 0 ?
                data.squat.stats.sets : 'No data';
            
            // Update deadlift stats
            document.getElementById('deadlift-max-weight').textContent = data.deadlift.stats.max_weight > 0 ?
                data.deadlift.stats.max_weight.toFixed(1) + ' lbs' : 'No data';
            document.getElementById('deadlift-sets').textContent = data.deadlift.stats.sets > 0 ?
                data.deadlift.stats.sets : 'No data';
            
            // Create progress charts
            createBigThreeProgressChart('bench-progress-chart', data.bench_press.progress, 'Bench Press');
            createBigThreeProgressChart('squat-progress-chart', data.squat.progress, 'Squat');
            createBigThreeProgressChart('deadlift-progress-chart', data.deadlift.progress, 'Deadlift');
        })
        .catch(error => {
            console.error('Error loading big three analysis data:', error);
            
            // Set error messages in the UI
            document.getElementById('bench-max-weight').textContent = 'Error';
            document.getElementById('bench-sets').textContent = 'Error';
            document.getElementById('squat-max-weight').textContent = 'Error';
            document.getElementById('squat-sets').textContent = 'Error';
            document.getElementById('deadlift-max-weight').textContent = 'Error';
            document.getElementById('deadlift-sets').textContent = 'Error';
            
            // Display error messages in the charts
            document.getElementById('bench-progress-chart').innerHTML = 
                '<div class="flex items-center justify-center h-full text-red-500">Error loading data</div>';
            document.getElementById('squat-progress-chart').innerHTML = 
                '<div class="flex items-center justify-center h-full text-red-500">Error loading data</div>';
            document.getElementById('deadlift-progress-chart').innerHTML = 
                '<div class="flex items-center justify-center h-full text-red-500">Error loading data</div>';
        });
}

// Load exercise data
function loadExerciseData() {
    // Load exercise frequency data
    fetch('./data_json/exercise_frequency.json')
        .then(response => response.json())
        .then(data => {
            createExerciseFrequencyChart(data);
        })
        .catch(error => console.error('Error loading exercise frequency data:', error));
    
    // Load exercise volume data
    fetch('./data_json/exercise_volume.json')
        .then(response => response.json())
        .then(data => {
            createExerciseVolumeChart(data);
        })
        .catch(error => console.error('Error loading exercise volume data:', error));
    
    // Load weight distribution data
    fetch('./data_json/weight_distribution.json')
        .then(response => response.json())
        .then(data => {
            createWeightDistributionChart(data);
        })
        .catch(error => console.error('Error loading weight distribution data:', error));
    
    // Load reps distribution data
    fetch('./data_json/reps_distribution.json')
        .then(response => response.json())
        .then(data => {
            createRepsDistributionChart(data);
        })
        .catch(error => console.error('Error loading reps distribution data:', error));
}

// Load category data
function loadCategoryData() {
    fetch('./data_json/category_analysis.json')
        .then(response => response.json())
        .then(data => {
            createCategoryDistributionChart(data.category_counts);
            createCategoryVolumeChart(data.category_volume);
            createCategoryWeightChart(data.category_weight);
            createCategoryRepsChart(data.category_reps);
        })
        .catch(error => console.error('Error loading category data:', error));
}

// Load workout balance data
function loadWorkoutBalanceData() {
    fetch('./data_json/workout_balance.json')
        .then(response => response.json())
        .then(data => {
            createWorkoutBalancePieChart(data);
            createWorkoutBalanceBarChart(data);
        })
        .catch(error => console.error('Error loading workout balance data:', error));
}

// Load personal records data
function loadPersonalRecords() {
    fetch('./data_json/personal_records.json')
        .then(response => response.json())
        .then(data => {
            const lifts = ['Bench Press (Barbell)', 'Squat (Barbell)', 'Deadlift (Barbell)', 'Overhead Press (Barbell)'];
            const liftIds = ['bench', 'squat', 'deadlift', 'ohp'];
            
            lifts.forEach((lift, index) => {
                const liftId = liftIds[index];
                const liftData = data.personal_records[lift];
                
                if (liftData && liftData.estimated_1rm > 0) {
                    document.getElementById(`${liftId}-current-max`).textContent = `${liftData.current_max_weight.toFixed(0)} lbs`;
                    document.getElementById(`${liftId}-estimated-1rm`).textContent = `${liftData.estimated_1rm.toFixed(0)} lbs`;
                    
                    if (liftData.best_set) {
                        document.getElementById(`${liftId}-best-set`).textContent = 
                            `${liftData.best_set.weight} lbs × ${liftData.best_set.reps} reps (${liftData.best_set.date})`;
                    }
                } else {
                    document.getElementById(`${liftId}-current-max`).textContent = 'No data';
                    document.getElementById(`${liftId}-estimated-1rm`).textContent = 'No data';
                    document.getElementById(`${liftId}-best-set`).textContent = 'No data available';
                }
            });
            
            // Store training data globally for tab switching
            window.trainingData = data;
            
            // Load default training recommendations (hypertrophy)
            loadTrainingRecommendations('hypertrophy');
        })
        .catch(error => console.error('Error loading personal records:', error));
}

// Load goal setting data
function loadGoalSetting() {
    fetch('./data_json/goal_setting.json')
        .then(response => response.json())
        .then(data => {
            const lifts = ['Bench Press (Barbell)', 'Squat (Barbell)', 'Deadlift (Barbell)', 'Overhead Press (Barbell)'];
            const liftIds = ['bench', 'squat', 'deadlift', 'ohp'];
            
            lifts.forEach((lift, index) => {
                const liftId = liftIds[index];
                const goalData = data.goals[lift];
                
                if (goalData && goalData.current_1rm > 0) {
                    document.getElementById(`${liftId}-baseline-1rm`).textContent = `${goalData.baseline_1rm.toFixed(0)} lbs`;
                    document.getElementById(`${liftId}-current-1rm`).textContent = `${goalData.current_1rm.toFixed(0)} lbs`;
                    document.getElementById(`${liftId}-goal-1rm`).textContent = `${goalData.goal_1rm.toFixed(0)} lbs`;
                    document.getElementById(`${liftId}-remaining`).textContent = `${goalData.remaining_lbs.toFixed(0)} lbs`;
                    document.getElementById(`${liftId}-goal-status`).textContent = goalData.status;
                    
                    // Update progress bar
                    const progressBar = document.getElementById(`${liftId}-progress-bar`);
                    const progressText = document.getElementById(`${liftId}-progress-text`);
                    const progressContainer = progressBar.parentElement; // This is the gray container div
                    
                    // Only show progress bar if there's meaningful progress (> 5%)
                    if (goalData.progress_percentage > 5) {
                        progressContainer.style.display = 'block';
                        progressText.style.display = 'block';
                        progressBar.style.width = `${goalData.progress_percentage}%`;
                        progressText.textContent = `${goalData.progress_percentage.toFixed(1)}% Complete`;
                        
                        // Color code progress bar based on progress
                        if (goalData.progress_percentage >= 75) {
                            progressBar.className = 'bg-green-600 h-2 rounded-full transition-all duration-300';
                        } else if (goalData.progress_percentage >= 50) {
                            progressBar.className = 'bg-yellow-500 h-2 rounded-full transition-all duration-300';
                        } else {
                            progressBar.className = 'bg-primary-600 h-2 rounded-full transition-all duration-300';
                        }
                    } else {
                        // Hide progress bar when progress is minimal or negative
                        progressContainer.style.display = 'none';
                        progressText.style.display = 'block';
                    }
                } else {
                    document.getElementById(`${liftId}-baseline-1rm`).textContent = 'No data';
                    document.getElementById(`${liftId}-current-1rm`).textContent = 'No data';
                    document.getElementById(`${liftId}-goal-1rm`).textContent = 'No data';
                    document.getElementById(`${liftId}-remaining`).textContent = 'No data';
                    document.getElementById(`${liftId}-goal-status`).textContent = 'No data available';
                    document.getElementById(`${liftId}-progress-text`).textContent = 'No data available';
                    
                    // Hide progress bar for no data
                    const progressBar = document.getElementById(`${liftId}-progress-bar`);
                    const progressContainer = progressBar.parentElement;
                    progressContainer.style.display = 'none';
                }
            });
            
            // Update motivation section
            document.getElementById('days-remaining').textContent = data.days_remaining;
            document.getElementById('motivation-message').textContent = data.motivation_message;
            
        })
        .catch(error => console.error('Error loading goal setting data:', error));
}

// Load training recommendations based on type
function loadTrainingRecommendations(type) {
    if (!window.trainingData) return;
    
    const container = document.getElementById('training-recommendations');
    const principles = window.trainingData.training_principles[type];
    const lifts = ['Bench Press (Barbell)', 'Squat (Barbell)', 'Deadlift (Barbell)', 'Overhead Press (Barbell)'];
    
    let html = `
        <div class="mb-6 p-4 bg-gray-50 rounded-lg">
            <h4 class="text-lg font-medium text-gray-900 mb-2">${principles.title}</h4>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                    <span class="font-medium text-gray-700">Intensity:</span>
                    <span class="text-gray-600">${principles.intensity}</span>
                </div>
                <div>
                    <span class="font-medium text-gray-700">Volume:</span>
                    <span class="text-gray-600">${principles.volume}</span>
                </div>
                <div>
                    <span class="font-medium text-gray-700">Frequency:</span>
                    <span class="text-gray-600">${principles.frequency}</span>
                </div>
            </div>
            <div class="mt-3 text-xs text-gray-500">
                <strong>Research:</strong> ${principles.research_note}
            </div>
        </div>
        
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
    `;
    
    lifts.forEach(lift => {
        const liftData = window.trainingData.personal_records[lift];
        const recommendation = liftData[`${type}_recommendation`];
        
        if (liftData && liftData.estimated_1rm > 0) {
            html += `
                <div class="bg-white border border-gray-200 rounded-lg p-4">
                    <h5 class="font-medium text-gray-900 mb-3">${lift.replace(' (Barbell)', '')}</h5>
                    <div class="space-y-2 text-sm">
                        <div class="flex justify-between">
                            <span class="text-gray-600">Weight Range:</span>
                            <span class="font-medium text-primary-600">${recommendation.weight_range}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600">Reps:</span>
                            <span class="font-medium">${recommendation.rep_range}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600">Sets:</span>
                            <span class="font-medium">${recommendation.sets}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600">Rest:</span>
                            <span class="font-medium">${recommendation.rest}</span>
                        </div>
                    </div>
                    <div class="mt-3 text-xs text-gray-500">
                        ${recommendation.description}
                    </div>
                </div>
            `;
        }
    });
    
    html += '</div>';
    container.innerHTML = html;
}

// Set active training tab
function setActiveTrainingTab(activeType) {
    const tabs = ['hypertrophy', 'strength', 'power'];
    
    tabs.forEach(type => {
        const tab = document.getElementById(`${type}-tab`);
        if (tab) {
            if (type === activeType) {
                tab.className = 'px-4 py-2 text-sm font-medium rounded-md bg-primary-100 text-primary-700 border border-primary-200';
            } else {
                tab.className = 'px-4 py-2 text-sm font-medium rounded-md bg-gray-100 text-gray-700 border border-gray-200';
            }
        }
    });
}

// Update month navigation state
function updateMonthNavigationState() {
    const prevBtn = document.getElementById('prev-month-btn');
    const nextBtn = document.getElementById('next-month-btn');
    
    // Disable previous button if at first month
    prevBtn.disabled = currentMonthIndex <= 0;
    prevBtn.classList.toggle('opacity-50', prevBtn.disabled);
    
    // Disable next button if at last month
    nextBtn.disabled = currentMonthIndex >= availableMonths.length - 1;
    nextBtn.classList.toggle('opacity-50', nextBtn.disabled);
}

// Navigate to previous month
function navigateToPreviousMonth() {
    if (currentMonthIndex > 0) {
        currentMonthIndex--;
        loadMonthlySummary(availableMonths[currentMonthIndex]);
        updateMonthNavigationState();
    }
}

// Navigate to next month
function navigateToNextMonth() {
    if (currentMonthIndex < availableMonths.length - 1) {
        currentMonthIndex++;
        loadMonthlySummary(availableMonths[currentMonthIndex]);
        updateMonthNavigationState();
    }
}

// Load and display the most recent workouts
function loadRecentWorkouts(daysCount = null, dateIndex = null) {
    // Update days count if provided
    if (daysCount !== null) {
        currentDaysCount = daysCount;
    }
    
    // Update date index if provided
    if (dateIndex !== null) {
        currentDateIndex = dateIndex;
    }
    
    // Show loading state
    const container = document.getElementById('recent-workouts-container');
    container.innerHTML = `
        <div class="col-span-3 flex justify-center items-center p-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
            <span class="ml-2 text-gray-600">Loading workouts...</span>
        </div>
    `;
    
    // Load or use cached workouts data
    if (allWorkoutsData === null) {
        // First load: fetch all workouts
        fetch('./data_json/recent_workouts.json')
            .then(response => response.json())
            .then(fetchedData => {
                allWorkoutsData = fetchedData; // Cache it
                displayWorkouts();
            })
            .catch(error => {
                console.error('Error loading recent workouts:', error);
                container.innerHTML = `
                    <div class="col-span-3 bg-white p-6 rounded-lg shadow-sm border border-gray-200 text-center">
                        <p class="text-red-500">Failed to load workout data</p>
                        <p class="text-sm text-gray-500 mt-2">Error: ${error.message}</p>
                    </div>
                `;
            });
    } else {
        // Use cached data
        displayWorkouts();
    }

    function displayWorkouts() {
        // Slice cached data for pagination
        const startIdx = currentDateIndex;
        const endIdx = startIdx + currentDaysCount;
        const data = allWorkoutsData.slice(startIdx, endIdx);

        console.log('Recent workouts data:', data);

        // Clear the loading placeholders
        container.innerHTML = '';

        if (!data || data.length === 0) {
            container.innerHTML = `
                <div class="col-span-3 bg-white p-6 rounded-lg shadow-sm border border-gray-200 text-center">
                    <p class="text-gray-500">No workout data available for this date range</p>
                </div>
            `;
            return;
        }

        // Iterate through each workout day
        data.forEach(day => {
                const dayCard = document.createElement('div');
                dayCard.className = 'bg-white p-4 rounded-lg shadow-sm border border-gray-200';
                
                let workoutList = '';
                
                // Add content for each workout
                day.workouts.forEach(workout => {
                    const exerciseList = workout.exercises.map(ex => {
                        // Create a detailed table for each set
                        const setDetails = ex.set_details.map((set, index) => {
                            // Style based on whether this is a PR
                            const prClass = set.is_pr ? 'bg-red-50 font-medium' : '';
                            
                            // PR badge
                            const isPR = set.is_pr ? 
                                '<span class="ml-1 text-xs font-medium bg-red-100 text-red-800 px-1.5 py-0.5 rounded">PR</span>' : 
                                '';
                            
                            // Set type display
                            const setTypeClass = set.set_type === 'warmup' ? 'text-gray-500 italic' : 'text-gray-900';
                            const setTypeLabel = set.set_type === 'warmup' ? ' (warmup)' : '';
                            
                            const notes = set.notes ? `<div class="text-xs text-gray-500">${set.notes}</div>` : '';
                            const weightDisplay = set.weight > 0 ? `${set.weight} lbs` : 'Bodyweight';
                            
                            return `
                                <tr class="border-t border-gray-100 ${prClass}">
                                    <td class="py-1 pr-2 text-xs ${setTypeClass}">${index + 1}${setTypeLabel}</td>
                                    <td class="py-1 px-2 text-xs ${setTypeClass}">${set.reps}</td>
                                    <td class="py-1 px-2 text-xs ${setTypeClass}">${weightDisplay}${isPR}</td>
                                </tr>
                                ${notes ? `<tr><td colspan="3" class="pb-1">${notes}</td></tr>` : ''}
                            `;
                        }).join('');
                        
                        return `
                            <li class="mb-3">
                                <div class="font-medium text-sm">${ex.name}</div>
                                <div class="text-xs text-gray-500 mb-1">
                                    ${ex.sets} sets, ${ex.total_reps} total reps, ${ex.avg_weight > 0 ? `${ex.avg_weight} lbs avg` : 'Bodyweight'}
                                </div>
                                <table class="w-full text-left">
                                    <thead>
                                        <tr class="text-xs text-gray-500">
                                            <th class="py-1 pr-2">Set</th>
                                            <th class="py-1 px-2">Reps</th>
                                            <th class="py-1 px-2">Weight</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${setDetails}
                                    </tbody>
                                </table>
                            </li>
                        `;
                    }).join('');
                    
                    workoutList += `
                        <div class="mb-4">
                            <h4 class="text-md font-semibold text-gray-800">${workout.name}</h4>
                            <p class="text-xs text-gray-500 mb-2">${workout.exercise_count} exercises, ${formatNumber(Math.round(workout.volume))} lbs total</p>
                            <ul class="ml-2">
                                ${exerciseList}
                            </ul>
                        </div>
                    `;
                });
                
                dayCard.innerHTML = `
                    <h3 class="text-lg font-bold text-gray-900 mb-3">${day.date}</h3>
                    ${workoutList}
                `;
                
                container.appendChild(dayCard);
            });

            // Update the date navigation text
            updateWorkoutDateNavigation();
        }
    }

// Load all available workout dates
function loadWorkoutDates() {
    fetch('./data_json/workout_dates.json')
        .then(response => response.json())
        .then(data => {
            console.log('Workout dates:', data);
            if (data && data.dates) {
                availableWorkoutDates = data.dates;
                // Reset to showing the most recent dates
                currentDateIndex = 0;
                updateWorkoutDateNavigation();
            }
        })
        .catch(error => {
            console.error('Error loading workout dates:', error);
        });
}

// Update the workout date navigation text and button states
function updateWorkoutDateNavigation() {
    const prevBtn = document.getElementById('prev-date-btn');
    const nextBtn = document.getElementById('next-date-btn');
    const display = document.getElementById('current-date-display');
    
    if (currentDateIndex === 0) {
        display.textContent = 'Latest Workouts';
    } else {
        const startIdx = currentDateIndex * currentDaysCount;
        const endIdx = Math.min(startIdx + currentDaysCount, availableWorkoutDates.length);
        if (startIdx < availableWorkoutDates.length) {
            const startDate = availableWorkoutDates[startIdx];
            const endDate = availableWorkoutDates[endIdx - 1] || startDate;
            display.textContent = `${endDate} to ${startDate}`;
        } else {
            display.textContent = 'No more workouts';
        }
    }
    
    // Update button states
    prevBtn.disabled = currentDateIndex <= 0;
    prevBtn.classList.toggle('text-gray-300', currentDateIndex <= 0);
    
    const hasMoreDates = (currentDateIndex + 1) * currentDaysCount < availableWorkoutDates.length;
    nextBtn.disabled = !hasMoreDates;
    nextBtn.classList.toggle('text-gray-300', !hasMoreDates);
}

// Load a specific range of workout dates
function loadCustomWorkoutRange() {
    loadRecentWorkouts(currentDaysCount, currentDateIndex);
}

// Navigate to previous set of workout dates
function navigateToPreviousWorkoutDates() {
    if (currentDateIndex > 0) {
        currentDateIndex--;
        loadCustomWorkoutRange();
    }
}

// Navigate to next set of workout dates
function navigateToNextWorkoutDates() {
    const maxIndex = Math.ceil(availableWorkoutDates.length / currentDaysCount) - 1;
    if (currentDateIndex < maxIndex) {
        currentDateIndex++;
        loadCustomWorkoutRange();
    }
}

// Set up event listeners
function setupEventListeners() {
    // Monthly navigation
    document.getElementById('prev-month-btn').addEventListener('click', navigateToPreviousMonth);
    document.getElementById('next-month-btn').addEventListener('click', navigateToNextMonth);
    
    // Workout date navigation
    document.getElementById('prev-date-btn').addEventListener('click', navigateToPreviousWorkoutDates);
    document.getElementById('next-date-btn').addEventListener('click', navigateToNextWorkoutDates);
    
    // Days count selector
    document.getElementById('workout-days-count').addEventListener('change', function() {
        const selectedValue = parseInt(this.value);
        currentDateIndex = 0; // Reset to first page
        loadRecentWorkouts(selectedValue);
    });
    
    // Exercise selection
    const exerciseSelect = document.getElementById('exercise-select');
    if (exerciseSelect) {
        exerciseSelect.addEventListener('change', function() {
            if (this.value) {
                loadExerciseDetails(this.value);
            } else {
                document.getElementById('exercise-details').classList.add('hidden');
            }
        });
    }
    
    // Category selection
    const categorySelect = document.getElementById('category-select');
    if (categorySelect) {
        categorySelect.addEventListener('change', function() {
            if (this.value) {
                loadCategoryExercises(this.value);
            } else {
                document.getElementById('category-exercises').classList.add('hidden');
            }
        });
    }
    
    // Training recommendation tabs
    const hypertrophyTab = document.getElementById('hypertrophy-tab');
    const strengthTab = document.getElementById('strength-tab');
    const powerTab = document.getElementById('power-tab');
    
    if (hypertrophyTab) {
        hypertrophyTab.addEventListener('click', function() {
            setActiveTrainingTab('hypertrophy');
            loadTrainingRecommendations('hypertrophy');
        });
    }
    
    if (strengthTab) {
        strengthTab.addEventListener('click', function() {
            setActiveTrainingTab('strength');
            loadTrainingRecommendations('strength');
        });
    }
    
    if (powerTab) {
        powerTab.addEventListener('click', function() {
            setActiveTrainingTab('power');
            loadTrainingRecommendations('power');
        });
    }
}

// Load exercise details
function loadExerciseDetails(exercise) {
    // Create URL-safe slug
    const slug = exercise.toLowerCase()
        .replace(' (', '_')
        .replace('(', '')
        .replace(')', '')
        .replace(' ', '_')
        .replace('/', '_')
        .replace('-', '_')
        .replace(',', '')
        .replace("'", '')
        .replace('"', '');

    fetch(`./data_json/exercise_${slug}.json`)
        .then(response => response.json())
        .then(data => {
            // Update exercise details
            document.getElementById('exercise-sets').textContent = data.stats.sets;
            document.getElementById('exercise-avg-weight').textContent = data.stats.avg_weight.toFixed(1) + ' lbs';
            document.getElementById('exercise-max-weight').textContent = data.stats.max_weight.toFixed(1) + ' lbs';
            document.getElementById('exercise-avg-reps').textContent = data.stats.avg_reps.toFixed(1);
            document.getElementById('exercise-max-reps').textContent = data.stats.max_reps.toFixed(0);
            document.getElementById('exercise-total-volume').textContent = formatNumber(Math.round(data.stats.total_volume));
            
            // Create set chart
            createExerciseSetChart(data.sets, exercise);
            
            // Show exercise details
            document.getElementById('exercise-details').classList.remove('hidden');
        })
        .catch(error => console.error('Error loading exercise details:', error));
}

// Load category exercises
function loadCategoryExercises(category) {
    const slug = category.toLowerCase();
    fetch(`./data_json/category_exercises_${slug}.json`)
        .then(response => response.json())
        .then(data => {
            // Create category exercises chart
            createCategoryExercisesChart(data, category);
            
            // Populate category exercises table
            const tableBody = document.getElementById('category-exercises-table');
            tableBody.innerHTML = '';
            
            data.forEach(item => {
                const row = document.createElement('tr');
                
                const exerciseCell = document.createElement('td');
                exerciseCell.className = 'px-6 py-4 whitespace-nowrap';
                exerciseCell.textContent = item.exercise;
                row.appendChild(exerciseCell);
                
                const volumeCell = document.createElement('td');
                volumeCell.className = 'px-6 py-4 whitespace-nowrap';
                volumeCell.textContent = formatNumber(Math.round(item.volume));
                row.appendChild(volumeCell);
                
                const avgWeightCell = document.createElement('td');
                avgWeightCell.className = 'px-6 py-4 whitespace-nowrap';
                avgWeightCell.textContent = item.avg_weight.toFixed(1) + ' lbs';
                row.appendChild(avgWeightCell);
                
                const maxWeightCell = document.createElement('td');
                maxWeightCell.className = 'px-6 py-4 whitespace-nowrap';
                maxWeightCell.textContent = item.max_weight.toFixed(1) + ' lbs';
                row.appendChild(maxWeightCell);
                
                const avgRepsCell = document.createElement('td');
                avgRepsCell.className = 'px-6 py-4 whitespace-nowrap';
                avgRepsCell.textContent = item.avg_reps.toFixed(1);
                row.appendChild(avgRepsCell);
                
                const maxRepsCell = document.createElement('td');
                maxRepsCell.className = 'px-6 py-4 whitespace-nowrap';
                maxRepsCell.textContent = item.max_reps.toFixed(0);
                row.appendChild(maxRepsCell);
                
                tableBody.appendChild(row);
            });
            
            // Show category exercises
            document.getElementById('category-exercises').classList.remove('hidden');
        })
        .catch(error => console.error('Error loading category exercises:', error));
}

// Create monthly top exercises chart
function createMonthlyTopExercisesChart(data) {
    const exercises = data.map(item => item.exercise);
    const volumes = data.map(item => item.volume);
    
    const trace = {
        x: exercises,
        y: volumes,
        type: 'bar',
        marker: {
            color: chartColors,
            line: {
                color: '#fff',
                width: 1
            }
        },
        width: 0.5, // Make bars thinner
        bargap: 0.3  // Add more gap between bars
    };
    
    const layout = {
        margin: { t: 10, r: 10, l: 70, b: 120 },
        xaxis: {
            tickangle: -45,
            automargin: true,
            tickfont: {
                size: 10 // Smaller font for x-axis labels
            }
        },
        yaxis: {
            title: 'Total Volume (Weight × Reps)'
        },
        autosize: true,
        height: 320,
        barmode: 'group',
        bargap: 0.3
    };
    
    const config = {
        responsive: true,
        displayModeBar: false
    };
    
    Plotly.newPlot('monthly-top-exercises-chart', [trace], layout, config);
}

// Create monthly volume chart
function createMonthlyVolumeChart(data) {
    const months = data.map(item => item.month);
    const volumes = data.map(item => item.volume);
    
    const trace = {
        x: months,
        y: volumes,
        type: 'bar',
        marker: {
            color: '#0ea5e9',
            line: {
                color: '#fff',
                width: 1
            }
        }
    };
    
    const layout = {
        margin: { t: 10, r: 10, l: 70, b: 50 },
        xaxis: {
            title: 'Month'
        },
        yaxis: {
            title: 'Total Volume (Weight × Reps)'
        }
    };
    
    Plotly.newPlot('monthly-volume-chart', [trace], layout, {responsive: true});
}

// Create monthly sets chart
function createMonthlySetsChart(data) {
    const months = data.map(item => item.month);
    const sets = data.map(item => item.sets);
    
    const trace = {
        x: months,
        y: sets,
        type: 'bar',
        marker: {
            color: '#8b5cf6',
            line: {
                color: '#fff',
                width: 1
            }
        }
    };
    
    const layout = {
        margin: { t: 10, r: 10, l: 50, b: 50 },
        xaxis: {
            title: 'Month'
        },
        yaxis: {
            title: 'Total Sets'
        }
    };
    
    Plotly.newPlot('monthly-sets-chart', [trace], layout, {responsive: true});
}

// Create monthly duration chart
function createMonthlyDurationChart(data) {
    const months = data.map(item => item.month);
    const durations = data.map(item => item.duration_minutes / 60); // Convert to hours
    
    const trace = {
        x: months,
        y: durations,
        type: 'bar',
        marker: {
            color: '#10b981',
            line: {
                color: '#fff',
                width: 1
            }
        }
    };
    
    const layout = {
        margin: { t: 10, r: 10, l: 50, b: 50 },
        xaxis: {
            title: 'Month'
        },
        yaxis: {
            title: 'Total Duration (Hours)'
        }
    };
    
    Plotly.newPlot('monthly-duration-chart', [trace], layout, {responsive: true});
}

// Create yearly analysis chart
function createYearlyAnalysisChart(data) {
    const years = data.map(item => item.year.toString());
    const workouts = data.map(item => item.workouts);
    const volumes = data.map(item => item.volume / 10000); // Scale down for better visualization
    const sets = data.map(item => item.sets / 100); // Scale down for better visualization
    
    const trace1 = {
        x: years,
        y: workouts,
        name: 'Workouts',
        type: 'bar',
        marker: {
            color: '#0ea5e9'
        }
    };
    
    const trace2 = {
        x: years,
        y: volumes,
        name: 'Volume (×10,000)',
        type: 'bar',
        marker: {
            color: '#ef4444'
        }
    };
    
    const trace3 = {
        x: years,
        y: sets,
        name: 'Sets (×100)',
        type: 'bar',
        marker: {
            color: '#8b5cf6'
        }
    };
    
    const layout = {
        margin: { t: 10, r: 10, l: 50, b: 50 },
        xaxis: {
            title: 'Year'
        },
        yaxis: {
            title: 'Count'
        },
        barmode: 'group',
        legend: {
            orientation: 'h',
            y: -0.2
        }
    };
    
    Plotly.newPlot('yearly-analysis-chart', [trace1, trace2, trace3], layout, {responsive: true});
}

// Create big three progress chart
function createBigThreeProgressChart(elementId, data, liftName) {
    if (!data || data.length === 0) {
        document.getElementById(elementId).innerHTML = '<div class="flex items-center justify-center h-full text-gray-500">No data available</div>';
        return;
    }
    
    // Sort data by date ascending for proper trend calculation
    data.sort((a, b) => new Date(a.date) - new Date(b.date));
    
    const dates = data.map(item => item.date);
    const maxWeights = data.map(item => item.max_weight);
    
    // Calculate 30-point moving average for trend line
    const movingAvgWeights = [];
    const windowSize = 30;
    
    for (let i = 0; i < maxWeights.length; i++) {
        let sum = 0;
        let count = 0;
        
        // Look at window_size points centered at current point
        for (let j = Math.max(0, i - Math.floor(windowSize/2)); 
             j <= Math.min(maxWeights.length - 1, i + Math.floor(windowSize/2)); j++) {
            sum += maxWeights[j];
            count++;
        }
        
        movingAvgWeights.push(sum / count);
    }
    
    // Set colors based on lift type
    const primaryColor = liftName === 'Bench Press' ? '#0ea5e9' : 
                         liftName === 'Squat' ? '#ef4444' : '#10b981';
    
    const secondaryColor = liftName === 'Bench Press' ? 'rgba(14, 165, 233, 0.2)' : 
                           liftName === 'Squat' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(16, 185, 129, 0.2)';
    
    // Create the main data trace
    const dataTrace = {
        x: dates,
        y: maxWeights,
        type: 'scatter',
        mode: 'markers',
        name: 'Max Weight',
        marker: {
            size: 8,
            color: primaryColor,
            line: {
                width: 1,
                color: 'white'
            }
        },
        hovertemplate: '%{y} lbs<br>%{x}<extra></extra>'
    };
    
    // Create trend line trace
    const trendTrace = {
        x: dates,
        y: movingAvgWeights,
        type: 'scatter',
        mode: 'lines',
        name: 'Trend',
        line: {
            color: primaryColor,
            width: 3,
            shape: 'spline',
            smoothing: 1
        },
        hoverinfo: 'skip'
    };
    
    // Create range area trace
    const rangeTrace = {
        x: dates.concat(dates.slice().reverse()),
        y: maxWeights.map(w => w * 0.85).concat(maxWeights.slice().reverse()),
        fill: 'toself',
        fillcolor: secondaryColor,
        line: { color: 'transparent' },
        showlegend: false,
        hoverinfo: 'skip',
        name: 'Range'
    };
    
    // Define y-axis ranges to be consistent across all three lifts
    const yaxisRanges = {
        'Bench Press': [120, 200],
        'Squat': [150, 300],
        'Deadlift': [180, 300]
    };
    
    const yRange = yaxisRanges[liftName] || [0, Math.max(...maxWeights) * 1.1];
    
    // Create layout with consistent y-axis and improved design
    const layout = {
        margin: { t: 10, r: 10, l: 45, b: 50 },
        xaxis: {
            title: 'Date',
            showgrid: true,
            gridcolor: '#f3f4f6',
            tickformat: '%b %Y',
            tickangle: -45,
            tickfont: { size: 10 },
            nticks: 6
        },
        yaxis: {
            title: 'Weight (lbs)',
            showgrid: true,
            gridcolor: '#f3f4f6',
            zeroline: false,
            range: yRange
        },
        showlegend: false,
        plot_bgcolor: 'white',
        hovermode: 'closest',
        shapes: [{
            // Draw horizontal line at the max weight
            type: 'line',
            x0: dates[0],
            x1: dates[dates.length - 1],
            y0: Math.max(...maxWeights),
            y1: Math.max(...maxWeights),
            line: {
                color: primaryColor,
                width: 1,
                dash: 'dot'
            }
        }],
        annotations: [{
            // Annotate the max weight
            x: dates[maxWeights.indexOf(Math.max(...maxWeights))],
            y: Math.max(...maxWeights),
            text: `PR: ${Math.max(...maxWeights)} lbs`,
            font: { color: primaryColor, size: 10 },
            showarrow: true,
            arrowhead: 1,
            arrowcolor: primaryColor,
            arrowsize: 0.8,
            arrowwidth: 1,
            ax: 0,
            ay: -20
        }]
    };
    
    Plotly.newPlot(elementId, [rangeTrace, dataTrace, trendTrace], layout, {
        responsive: true, 
        displayModeBar: false
    });
}

// Create exercise frequency chart
function createExerciseFrequencyChart(data) {
    const exercises = data.map(item => item.exercise);
    const counts = data.map(item => item.count);
    const colors = data.map((item, index) => enhancedChartColors[index % enhancedChartColors.length]);
    
    const trace = {
        x: exercises,
        y: counts,
        type: 'bar',
        marker: {
            color: colors,
            line: {
                color: '#fff',
                width: 2
            },
            opacity: 0.8
        },
        hovertemplate: '<b>%{x}</b><br>Sets: %{y}<extra></extra>',
        textposition: 'outside',
        textfont: {
            size: 10,
            color: '#374151'
        }
    };
    
    const layout = {
        margin: { t: 20, r: 20, l: 60, b: 140 },
        xaxis: {
            tickangle: -45,
            automargin: true,
            title: {
                text: 'Exercise',
                font: { size: 14, color: '#374151' }
            },
            tickfont: { size: 11 },
            gridcolor: '#f3f4f6'
        },
        yaxis: {
            title: {
                text: 'Number of Sets',
                font: { size: 14, color: '#374151' }
            },
            tickfont: { size: 12 },
            gridcolor: '#f3f4f6'
        },
        plot_bgcolor: '#fafafa',
        paper_bgcolor: '#ffffff',
        font: { family: 'Inter, system-ui, sans-serif' }
    };
    
    Plotly.newPlot('exercise-frequency-chart', [trace], layout, {responsive: true});
}

// Create exercise volume chart
function createExerciseVolumeChart(data) {
    const exercises = data.map(item => item.exercise);
    const volumes = data.map(item => item.volume);
    const colors = data.map((item, index) => enhancedChartColors[index % enhancedChartColors.length]);
    
    const trace = {
        x: exercises,
        y: volumes,
        type: 'bar',
        marker: {
            color: colors,
            line: {
                color: '#fff',
                width: 2
            },
            opacity: 0.8
        },
        hovertemplate: '<b>%{x}</b><br>Volume: %{y:,.0f}<extra></extra>',
        textposition: 'outside',
        textfont: {
            size: 10,
            color: '#374151'
        }
    };
    
    const layout = {
        margin: { t: 20, r: 20, l: 80, b: 140 },
        xaxis: {
            tickangle: -45,
            automargin: true,
            title: {
                text: 'Exercise',
                font: { size: 14, color: '#374151' }
            },
            tickfont: { size: 11 },
            gridcolor: '#f3f4f6'
        },
        yaxis: {
            title: {
                text: 'Total Volume (Weight × Reps)',
                font: { size: 14, color: '#374151' }
            },
            tickfont: { size: 12 },
            gridcolor: '#f3f4f6'
        },
        plot_bgcolor: '#fafafa',
        paper_bgcolor: '#ffffff',
        font: { family: 'Inter, system-ui, sans-serif' }
    };
    
    Plotly.newPlot('exercise-volume-chart', [trace], layout, {responsive: true});
}

// Create weight distribution chart
function createWeightDistributionChart(data) {
    const trace = {
        x: data,
        type: 'histogram',
        marker: {
            color: '#0ea5e9',
            line: {
                color: '#fff',
                width: 1
            }
        },
        nbinsx: 20
    };
    
    const layout = {
        margin: { t: 10, r: 10, l: 50, b: 50 },
        xaxis: {
            title: 'Weight (lbs)'
        },
        yaxis: {
            title: 'Frequency'
        }
    };
    
    Plotly.newPlot('weight-distribution-chart', [trace], layout, {responsive: true});
}

// Create reps distribution chart
function createRepsDistributionChart(data) {
    const trace = {
        x: data,
        type: 'histogram',
        marker: {
            color: '#8b5cf6',
            line: {
                color: '#fff',
                width: 1
            }
        },
        nbinsx: 15
    };
    
    const layout = {
        margin: { t: 10, r: 10, l: 50, b: 50 },
        xaxis: {
            title: 'Reps'
        },
        yaxis: {
            title: 'Frequency'
        }
    };
    
    Plotly.newPlot('reps-distribution-chart', [trace], layout, {responsive: true});
}

// Create category distribution chart
function createCategoryDistributionChart(data) {
    const categories = data.map(item => getCategoryDisplayName(item.category));
    const counts = data.map(item => item.count);
    const colors = data.map((item, index) => {
        const baseColor = categoryColors[item.category];
        return createGradientColor(baseColor, index, data.length);
    });
    
    const trace = {
        x: categories,
        y: counts,
        type: 'bar',
        marker: {
            color: colors,
            line: {
                color: '#fff',
                width: 2
            },
            opacity: 0.8
        },
        hovertemplate: '<b>%{x}</b><br>Sets: %{y}<extra></extra>',
        textposition: 'outside',
        textfont: {
            size: 12,
            color: '#374151'
        }
    };
    
    const layout = {
        margin: { t: 20, r: 20, l: 60, b: 80 },
        xaxis: {
            title: {
                text: 'Category',
                font: { size: 14, color: '#374151' }
            },
            tickfont: { size: 12 },
            gridcolor: '#f3f4f6'
        },
        yaxis: {
            title: {
                text: 'Number of Sets',
                font: { size: 14, color: '#374151' }
            },
            tickfont: { size: 12 },
            gridcolor: '#f3f4f6'
        },
        plot_bgcolor: '#fafafa',
        paper_bgcolor: '#ffffff',
        font: { family: 'Inter, system-ui, sans-serif' }
    };
    
    Plotly.newPlot('category-distribution-chart', [trace], layout, {responsive: true});
}

// Create category volume chart
function createCategoryVolumeChart(data) {
    const categories = data.map(item => getCategoryDisplayName(item.category));
    const volumes = data.map(item => item.volume);
    const colors = data.map((item, index) => {
        const baseColor = categoryColors[item.category];
        return createGradientColor(baseColor, index, data.length);
    });
    
    const trace = {
        x: categories,
        y: volumes,
        type: 'bar',
        marker: {
            color: colors,
            line: {
                color: '#fff',
                width: 2
            },
            opacity: 0.8
        },
        hovertemplate: '<b>%{x}</b><br>Volume: %{y:,.0f}<extra></extra>',
        textposition: 'outside',
        textfont: {
            size: 12,
            color: '#374151'
        }
    };
    
    const layout = {
        margin: { t: 20, r: 20, l: 80, b: 80 },
        xaxis: {
            title: {
                text: 'Category',
                font: { size: 14, color: '#374151' }
            },
            tickfont: { size: 12 },
            gridcolor: '#f3f4f6'
        },
        yaxis: {
            title: {
                text: 'Total Volume (Weight × Reps)',
                font: { size: 14, color: '#374151' }
            },
            tickfont: { size: 12 },
            gridcolor: '#f3f4f6'
        },
        plot_bgcolor: '#fafafa',
        paper_bgcolor: '#ffffff',
        font: { family: 'Inter, system-ui, sans-serif' }
    };
    
    Plotly.newPlot('category-volume-chart', [trace], layout, {responsive: true});
}

// Create category weight chart
function createCategoryWeightChart(data) {
    const categories = data.map(item => getCategoryDisplayName(item.category));
    const weights = data.map(item => item.weight);
    const colors = data.map((item, index) => {
        const baseColor = categoryColors[item.category];
        return createGradientColor(baseColor, index, data.length);
    });
    
    const trace = {
        x: categories,
        y: weights,
        type: 'bar',
        marker: {
            color: colors,
            line: {
                color: '#fff',
                width: 2
            },
            opacity: 0.8
        },
        hovertemplate: '<b>%{x}</b><br>Avg Weight: %{y:.1f} lbs<extra></extra>',
        textposition: 'outside',
        textfont: {
            size: 12,
            color: '#374151'
        }
    };
    
    const layout = {
        margin: { t: 20, r: 20, l: 70, b: 80 },
        xaxis: {
            title: {
                text: 'Category',
                font: { size: 14, color: '#374151' }
            },
            tickfont: { size: 12 },
            gridcolor: '#f3f4f6'
        },
        yaxis: {
            title: {
                text: 'Average Weight (lbs)',
                font: { size: 14, color: '#374151' }
            },
            tickfont: { size: 12 },
            gridcolor: '#f3f4f6'
        },
        plot_bgcolor: '#fafafa',
        paper_bgcolor: '#ffffff',
        font: { family: 'Inter, system-ui, sans-serif' }
    };
    
    Plotly.newPlot('category-weight-chart', [trace], layout, {responsive: true});
}

// Create category reps chart
function createCategoryRepsChart(data) {
    const categories = data.map(item => getCategoryDisplayName(item.category));
    const reps = data.map(item => item.reps);
    const colors = data.map((item, index) => {
        const baseColor = categoryColors[item.category];
        return createGradientColor(baseColor, index, data.length);
    });
    
    const trace = {
        x: categories,
        y: reps,
        type: 'bar',
        marker: {
            color: colors,
            line: {
                color: '#fff',
                width: 2
            },
            opacity: 0.8
        },
        hovertemplate: '<b>%{x}</b><br>Avg Reps: %{y:.1f}<extra></extra>',
        textposition: 'outside',
        textfont: {
            size: 12,
            color: '#374151'
        }
    };
    
    const layout = {
        margin: { t: 20, r: 20, l: 60, b: 80 },
        xaxis: {
            title: {
                text: 'Category',
                font: { size: 14, color: '#374151' }
            },
            tickfont: { size: 12 },
            gridcolor: '#f3f4f6'
        },
        yaxis: {
            title: {
                text: 'Average Reps',
                font: { size: 14, color: '#374151' }
            },
            tickfont: { size: 12 },
            gridcolor: '#f3f4f6'
        },
        plot_bgcolor: '#fafafa',
        paper_bgcolor: '#ffffff',
        font: { family: 'Inter, system-ui, sans-serif' }
    };
    
    Plotly.newPlot('category-reps-chart', [trace], layout, {responsive: true});
}

// Create exercise set chart
function createExerciseSetChart(data, exerciseName) {
    const sets = data.map(item => item.set);
    const weights = data.map(item => item.weight);
    const reps = data.map(item => item.reps);
    const volumes = data.map(item => item.volume);
    
    const trace1 = {
        x: sets,
        y: weights,
        name: 'Weight (lbs)',
        type: 'scatter',
        mode: 'lines+markers',
        marker: {
            color: '#0ea5e9',
            size: 8
        },
        line: {
            width: 3
        }
    };
    
    const trace2 = {
        x: sets,
        y: reps,
        name: 'Reps',
        type: 'scatter',
        mode: 'lines+markers',
        marker: {
            color: '#8b5cf6',
            size: 8
        },
        line: {
            width: 3
        },
        yaxis: 'y2'
    };
    
    const trace3 = {
        x: sets,
        y: volumes,
        name: 'Volume',
        type: 'scatter',
        mode: 'lines+markers',
        marker: {
            color: '#ef4444',
            size: 8
        },
        line: {
            width: 3
        },
        yaxis: 'y3'
    };
    
    const layout = {
        title: {
            text: `${exerciseName} - Set Progression`,
            font: {
                size: 16
            }
        },
        margin: { t: 40, r: 70, l: 50, b: 50 },
        xaxis: {
            title: 'Set',
            tickmode: 'linear'
        },
        yaxis: {
            title: 'Weight (lbs)',
            titlefont: { color: '#0ea5e9' },
            tickfont: { color: '#0ea5e9' }
        },
        yaxis2: {
            title: 'Reps',
            titlefont: { color: '#8b5cf6' },
            tickfont: { color: '#8b5cf6' },
            overlaying: 'y',
            side: 'right',
            position: 0.85
        },
        yaxis3: {
            title: 'Volume',
            titlefont: { color: '#ef4444' },
            tickfont: { color: '#ef4444' },
            overlaying: 'y',
            side: 'right'
        },
        legend: {
            orientation: 'h',
            y: -0.2
        }
    };
    
    Plotly.newPlot('exercise-set-chart', [trace1, trace2, trace3], layout, {responsive: true});
}

// Create category exercises chart
function createCategoryExercisesChart(data, categoryName) {
    const exercises = data.map(item => item.exercise);
    const volumes = data.map(item => item.volume);
    const colors = data.map((item, index) => enhancedChartColors[index % enhancedChartColors.length]);
    
    const trace = {
        x: exercises,
        y: volumes,
        type: 'bar',
        marker: {
            color: colors,
            line: {
                color: '#fff',
                width: 2
            },
            opacity: 0.8
        },
        hovertemplate: '<b>%{x}</b><br>Volume: %{y:,.0f}<extra></extra>',
        textposition: 'outside',
        textfont: {
            size: 10,
            color: '#374151'
        }
    };
    
    const categoryDisplayName = getCategoryDisplayName(categoryName);
    const layout = {
        title: {
            text: `Top ${categoryDisplayName} Exercises by Volume`,
            font: {
                size: 16,
                color: '#374151'
            }
        },
        margin: { t: 50, r: 20, l: 80, b: 140 },
        xaxis: {
            tickangle: -45,
            automargin: true,
            title: {
                text: 'Exercise',
                font: { size: 14, color: '#374151' }
            },
            tickfont: { size: 11 },
            gridcolor: '#f3f4f6'
        },
        yaxis: {
            title: {
                text: 'Total Volume (Weight × Reps)',
                font: { size: 14, color: '#374151' }
            },
            tickfont: { size: 12 },
            gridcolor: '#f3f4f6'
        },
        plot_bgcolor: '#fafafa',
        paper_bgcolor: '#ffffff',
        font: { family: 'Inter, system-ui, sans-serif' }
    };
    
    Plotly.newPlot('category-exercises-chart', [trace], layout, {responsive: true});
}

// Create workout balance pie chart
function createWorkoutBalancePieChart(data) {
    const categories = data.map(item => getCategoryDisplayName(item.category));
    const percentages = data.map(item => item.percentage);
    const colors = data.map(item => categoryColors[item.category]);
    
    const trace = {
        labels: categories,
        values: percentages,
        type: 'pie',
        marker: {
            colors: colors,
            line: {
                color: '#fff',
                width: 2
            }
        },
        textinfo: 'label+percent',
        insidetextorientation: 'radial',
        hovertemplate: '<b>%{label}</b><br>%{percent}<br>Volume: %{value:.1f}%<extra></extra>',
        textfont: {
            size: 12,
            color: '#374151'
        }
    };
    
    const layout = {
        margin: { t: 20, r: 20, l: 20, b: 20 },
        showlegend: false,
        plot_bgcolor: '#fafafa',
        paper_bgcolor: '#ffffff',
        font: { family: 'Inter, system-ui, sans-serif' }
    };
    
    Plotly.newPlot('workout-balance-pie-chart', [trace], layout, {responsive: true});
}

// Create workout balance bar chart
function createWorkoutBalanceBarChart(data) {
    const categories = data.map(item => getCategoryDisplayName(item.category));
    const percentages = data.map(item => item.percentage);
    const colors = data.map(item => categoryColors[item.category]);
    
    const trace = {
        x: percentages,
        y: categories,
        type: 'bar',
        orientation: 'h',
        marker: {
            color: colors,
            line: {
                color: '#fff',
                width: 2
            },
            opacity: 0.8
        },
        hovertemplate: '<b>%{y}</b><br>Volume: %{x:.1f}%<extra></extra>',
        textposition: 'outside',
        textfont: {
            size: 12,
            color: '#374151'
        }
    };
    
    const layout = {
        margin: { t: 20, r: 20, l: 120, b: 60 },
        xaxis: {
            title: {
                text: 'Percentage of Total Volume',
                font: { size: 14, color: '#374151' }
            },
            ticksuffix: '%',
            tickfont: { size: 12 },
            gridcolor: '#f3f4f6'
        },
        yaxis: {
            title: {
                text: 'Category',
                font: { size: 14, color: '#374151' }
            },
            tickfont: { size: 12 }
        },
        plot_bgcolor: '#fafafa',
        paper_bgcolor: '#ffffff',
        font: { family: 'Inter, system-ui, sans-serif' }
    };
    
    Plotly.newPlot('workout-balance-bar-chart', [trace], layout, {responsive: true});
}

// Function to get category display name with emoji
function getCategoryDisplayName(category) {
    const emoji = categoryEmojis[category] || '📊';
    return `${emoji} ${category}`;
}

// Function to create gradient colors for bars
function createGradientColor(baseColor, index, total) {
    const opacity = 0.7 + (0.3 * (index / total));
    return baseColor + Math.round(opacity * 255).toString(16).padStart(2, '0');
} 
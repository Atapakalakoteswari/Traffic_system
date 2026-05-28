import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, VotingRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

def train_models():
    print("="*70)
    print("TRAFFIC PREDICTION SYSTEM - MODEL TRAINING (No TensorFlow)")
    print("="*70)
    print("\nLoading dataset...")
    df = pd.read_csv('../dataset/traffic_data.csv')
    print(f"Loaded {len(df)} records")
    
    print("\nCleaning data...")
    initial_len = len(df)
    df = df.dropna()
    df = df.drop_duplicates()
    print(f"Removed {initial_len - len(df)} duplicate/missing records")
    print(f"After cleaning: {len(df)} records")
    
    print("\nEncoding categorical variables...")
    le_weather = LabelEncoder()
    df['weather_encoded'] = le_weather.fit_transform(df['weather'])
    
    weather_mapping = dict(zip(le_weather.classes_, le_weather.transform(le_weather.classes_)))
    print(f"Weather encoding: {weather_mapping}")
    
    features = ['hour', 'day_of_week', 'month', 'is_weekend', 'is_rush_hour',
               'temperature', 'precipitation', 'road_construction', 'accident',
               'weather_encoded', 'traffic_volume']
    
    target_congestion = 'congestion_level'
    target_travel_time = 'travel_time'
    
    X = df[features]
    y_congestion = df[target_congestion]
    y_travel_time = df[target_travel_time]
    
    print(f"\nFeatures: {features}")
    print(f"Target (Congestion): {target_congestion}")
    print(f"Target (Travel Time): {target_travel_time}")
    
    print("\nSplitting data...")
    X_train, X_test, y_congestion_train, y_congestion_test = train_test_split(
        X, y_congestion, test_size=0.2, random_state=42, stratify=y_congestion
    )
    X_train_time, X_test_time, y_travel_train, y_travel_test = train_test_split(
        X, y_travel_time, test_size=0.2, random_state=42
    )
    print(f"Training set: {X_train.shape[0]} samples")
    print(f"Test set: {X_test.shape[0]} samples")

    print("\nScaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    X_train_time_scaled = scaler.transform(X_train_time)
    X_test_time_scaled = scaler.transform(X_test_time)
    print("Features scaled successfully")
    
    results = {}
    
    print("\n" + "="*70)
    print("CONGESTION LEVEL PREDICTION MODELS")
    print("="*70)
    
    print("\n1. Training Decision Tree...")
    dt_model = DecisionTreeRegressor(
        max_depth=10, 
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42
    )
    dt_model.fit(X_train_scaled, y_congestion_train)
    dt_pred = dt_model.predict(X_test_scaled)
    dt_rmse = np.sqrt(mean_squared_error(y_congestion_test, dt_pred))
    dt_r2 = r2_score(y_congestion_test, dt_pred)
    dt_mae = mean_absolute_error(y_congestion_test, dt_pred)
    results['Decision Tree'] = {'RMSE': dt_rmse, 'R2': dt_r2, 'MAE': dt_mae}
    print(f"    RMSE: {dt_rmse:.4f}")
    print(f"    R² Score: {dt_r2:.4f}")
    print(f"    MAE: {dt_mae:.4f}")
    
    print("\n 2. Training Random Forest...")
    rf_model = RandomForestRegressor(
        n_estimators=150,
        max_depth=12,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    rf_model.fit(X_train_scaled, y_congestion_train)
    rf_pred = rf_model.predict(X_test_scaled)
    rf_rmse = np.sqrt(mean_squared_error(y_congestion_test, rf_pred))
    rf_r2 = r2_score(y_congestion_test, rf_pred)
    rf_mae = mean_absolute_error(y_congestion_test, rf_pred)
    results['Random Forest'] = {'RMSE': rf_rmse, 'R2': rf_r2, 'MAE': rf_mae}
    print(f"    RMSE: {rf_rmse:.4f}")
    print(f"    R² Score: {rf_r2:.4f}")
    print(f"    MAE: {rf_mae:.4f}")
    
    print("\n3. Training Gradient Boosting...")
    gb_model = GradientBoostingRegressor(
        n_estimators=150,
        learning_rate=0.1,
        max_depth=5,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42
    )
    gb_model.fit(X_train_scaled, y_congestion_train)
    gb_pred = gb_model.predict(X_test_scaled)
    gb_rmse = np.sqrt(mean_squared_error(y_congestion_test, gb_pred))
    gb_r2 = r2_score(y_congestion_test, gb_pred)
    gb_mae = mean_absolute_error(y_congestion_test, gb_pred)
    results['Gradient Boosting'] = {'RMSE': gb_rmse, 'R2': gb_r2, 'MAE': gb_mae}
    print(f"    RMSE: {gb_rmse:.4f}")
    print(f"    R² Score: {gb_r2:.4f}")
    print(f"    MAE: {gb_mae:.4f}")
    
    print("\n 4. Training Ridge Regression...")
    ridge_model = Ridge(alpha=1.0, random_state=42)
    ridge_model.fit(X_train_scaled, y_congestion_train)
    ridge_pred = ridge_model.predict(X_test_scaled)
    ridge_rmse = np.sqrt(mean_squared_error(y_congestion_test, ridge_pred))
    ridge_r2 = r2_score(y_congestion_test, ridge_pred)
    ridge_mae = mean_absolute_error(y_congestion_test, ridge_pred)
    results['Ridge Regression'] = {'RMSE': ridge_rmse, 'R2': ridge_r2, 'MAE': ridge_mae}
    print(f"    RMSE: {ridge_rmse:.4f}")
    print(f"    R² Score: {ridge_r2:.4f}")
    print(f"    MAE: {ridge_mae:.4f}")
    

    print("\n Performing Cross-Validation on Random Forest...")
    cv_scores = cross_val_score(rf_model, X_train_scaled, y_congestion_train, cv=5, scoring='r2')
    print(f"    Cross-validation R² scores: {cv_scores}")
    print(f"    Mean CV R²: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    print("\n" + "="*70)
    print("TRAVEL TIME PREDICTION MODELS")
    print("="*70)
    

    print("\n 5. Training Random Forest for Travel Time...")
    rf_time_model = RandomForestRegressor(
        n_estimators=150,
        max_depth=12,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    rf_time_model.fit(X_train_time_scaled, y_travel_train)
    rf_time_pred = rf_time_model.predict(X_test_time_scaled)
    rf_time_rmse = np.sqrt(mean_squared_error(y_travel_test, rf_time_pred))
    rf_time_r2 = r2_score(y_travel_test, rf_time_pred)
    rf_time_mae = mean_absolute_error(y_travel_test, rf_time_pred)
    results['RF (Travel Time)'] = {'RMSE': rf_time_rmse, 'R2': rf_time_r2, 'MAE': rf_time_mae}
    print(f"    RMSE: {rf_time_rmse:.4f} minutes")
    print(f"    R² Score: {rf_time_r2:.4f}")
    print(f"    MAE: {rf_time_mae:.4f} minutes")
    
    print("\n 6. Training Gradient Boosting for Travel Time...")
    gb_time_model = GradientBoostingRegressor(
        n_estimators=150,
        learning_rate=0.1,
        max_depth=5,
        random_state=42
    )
    gb_time_model.fit(X_train_time_scaled, y_travel_train)
    gb_time_pred = gb_time_model.predict(X_test_time_scaled)
    gb_time_rmse = np.sqrt(mean_squared_error(y_travel_test, gb_time_pred))
    gb_time_r2 = r2_score(y_travel_test, gb_time_pred)
    gb_time_mae = mean_absolute_error(y_travel_test, gb_time_pred)
    results['GB (Travel Time)'] = {'RMSE': gb_time_rmse, 'R2': gb_time_r2, 'MAE': gb_time_mae}
    print(f"    RMSE: {gb_time_rmse:.4f} minutes")
    print(f"    R² Score: {gb_time_r2:.4f}")
    print(f"    MAE: {gb_time_mae:.4f} minutes")
    
    print("\n7. Training Voting Ensemble for Travel Time...")
    voting_model = VotingRegressor([
        ('rf', rf_time_model),
        ('gb', gb_time_model),
        ('ridge', Ridge(alpha=1.0))
    ])
    voting_model.fit(X_train_time_scaled, y_travel_train)
    voting_pred = voting_model.predict(X_test_time_scaled)
    voting_rmse = np.sqrt(mean_squared_error(y_travel_test, voting_pred))
    voting_r2 = r2_score(y_travel_test, voting_pred)
    voting_mae = mean_absolute_error(y_travel_test, voting_pred)
    results['Voting Ensemble'] = {'RMSE': voting_rmse, 'R2': voting_r2, 'MAE': voting_mae}
    print(f"    RMSE: {voting_rmse:.4f} minutes")
    print(f"    R² Score: {voting_r2:.4f}")
    print(f"    MAE: {voting_mae:.4f} minutes")
    
    print("\n" + "="*70)
    print(" FEATURE IMPORTANCE ANALYSIS")
    print("="*70)
    
    feature_importance = pd.DataFrame({
        'feature': features,
        'importance': rf_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nTop 5 Most Important Features:")
    for idx, row in feature_importance.head().iterrows():
        print(f"   • {row['feature']}: {row['importance']:.4f}")
    
    print("\n" + "="*70)
    print(" SAVING MODELS")
    print("="*70)
    

    os.makedirs('../traffic_project/traffic_app/models', exist_ok=True)
    
    joblib.dump(rf_model, '../traffic_project/traffic_app/models/congestion_model.pkl')
    print("Random Forest model saved (Congestion Prediction)")
    
    joblib.dump(rf_time_model, '../traffic_project/traffic_app/models/travel_time_model.pkl')
    print("Random Forest model saved (Travel Time Prediction)")
    
    joblib.dump(scaler, '../traffic_project/traffic_app/models/scaler.pkl')
    print("Standard Scaler saved")
    
    joblib.dump(le_weather, '../traffic_project/traffic_app/models/label_encoder.pkl')
    print("Label Encoder saved")
    
    joblib.dump(features, '../traffic_project/traffic_app/models/feature_names.pkl')
    print("Feature names saved")
    
    print("\n" + "="*70)
    print("MODEL PERFORMANCE SUMMARY")
    print("="*70)
    
    results_df = pd.DataFrame(results).T
    print(results_df.round(4))
    
    print("\n" + "="*70)
    print(f"BEST MODEL FOR CONGESTION: Random Forest")
    print(f"   → R² Score: {rf_r2:.4f}")
    print(f"   → Accuracy: {rf_r2*100:.1f}%")
    
    print(f"\nBEST MODEL FOR TRAVEL TIME: Random Forest")
    print(f"   → R² Score: {rf_time_r2:.4f}")
    print(f"   → Accuracy: {rf_time_r2*100:.1f}%")
    print(f"   → Average Error: {rf_time_mae:.1f} minutes")
    print("="*70)

    print("\nTEST PREDICTION EXAMPLE")
    print("-"*70)
    sample_input = X_test.iloc[0:1]
    sample_scaled = scaler.transform(sample_input)
    sample_congestion = rf_model.predict(sample_scaled)[0]
    sample_travel = rf_time_model.predict(sample_scaled)[0]
    
    print(f"Input features:")
    for feature, value in sample_input.iloc[0].items():
        print(f"  {feature}: {value}")
    print(f"\nPredicted Congestion Level: {round(sample_congestion)} ({['Low','Medium','High','Severe'][round(sample_congestion)]})")
    print(f"Predicted Travel Time: {sample_travel:.1f} minutes")
    print("-"*70)
    
    return results_df

if __name__ == "__main__":
    results = train_models()
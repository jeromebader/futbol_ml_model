
# Reentrene un nuevo el modelo con los datos disponibles en la carpeta data, que guarde ese modelo reentrenado, devolviendo en la respuesta la media del MAE de un cross validation con el nuevo modelo
@app.route('/v1/retrain', methods=['PUT'])
def retrain():
    df = pd.read_csv('data/Advertising.csv', index_col=0)
    X = df.drop(columns=['sales'])
    y = df['sales']

    model = pickle.load(open('data/advertising_model','rb'))
    model.fit(X,y)
    pickle.dump(model, open('data/advertising_model_v1','wb'))

    scores = cross_val_score(model, X, y, cv=10, scoring='neg_mean_absolute_error')

    return "New model retrained and saved as advertising_model_v1. The results of MAE with cross validation of 10 folds is: " + str(abs(round(scores.mean(),2)))


app.run()
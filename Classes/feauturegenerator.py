class FeatureGenetator():
    """Генерация новых фич"""

    def __init__(self):
        self.binary_to_numbers = None


    def fit(self, X):

        X = X.copy()

        # Binary features
        self.binary_to_numbers = {'A': 0, 'B': 1}


    def transform(self, X):
        
        # Binary features
        X['Ecology_2'] = X['Ecology_2'].map(self.binary_to_numbers)  # self.binary_to_numbers = {'A': 0, 'B': 1}
        X['Ecology_3'] = X['Ecology_3'].map(self.binary_to_numbers)
        X['Shops_2'] = X['Shops_2'].map(self.binary_to_numbers)


        #HouseFloor_outlier
        X['HouseFloor_outlier'] = 0
        X.loc[X['HouseFloor'] < X['Floor'], 'HouseFloor_outlier'] = 1
        X.loc[X['HouseFloor'] == 0, 'HouseFloor_outlier'] = 1


        # первый/последний этаж
		X['FirstLastFloor'] = 0
		X.loc[(X['Floor'] == 1) | (X['Floor'] == X['HouseFloor']), 'FirstLastFloor'] = 1

		# средняя стоимость метра в районе
		med_price_by_district = X.groupby('DistrictId', as_index=False).agg({'Price':'median'}).rename(columns={'Price':'MedPriceByDistrict'})
		X = X.merge(med_price_by_district, on='DistrictId', how='left')

        return X


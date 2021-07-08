class DataPreprocessing:
    """Подготовка исходных данных"""

    def __init__(self):
        """Параметры класса"""
        self.medians = None
        self.kitchen_square_quantile = None
        self.square_quantile_025 = None
        self.square_quantile_975 = None
        self.lifesquare_quantile_025 = None
        self.lifesquare_quantile_975 = None
        self.med_square_by_rooms = None
        self.med_square_by_rooms_district = None
        self.men_lifesquare_square_cat = None


    def fit(self, X):
        """Сохранение статистик"""       
        # Расчет медиан
        self.medians = X.median()
        self.square_quantile_975 = X['Square'].quantile(.975)
        self.square_quantile_025 = X['Square'].quantile(.025)
        self.lifesquare_quantile_025 = X['LifeSquare'].quantile(.025)
        self.lifesquare_quantile_975 = X['LifeSquare'].quantile(.975)
        self.kitchen_square_quantile = X['KitchenSquare'].quantile(.975)

        self.med_square_by_rooms_district = X.groupby(['Rooms','DistrictId'], as_index=False).agg({'Square':'median'}).\
                                            rename(columns={'Square':'MedSquareByRoomsDistrictId'})
        self.med_square_by_rooms = X.groupby('Rooms', as_index=False).agg({'Square':'median'}).\
                                                    rename(columns={'Square':'MedSquareByRooms'})


    
    def transform(self, X):
        """Трансформация данных"""

        # Rooms
        X['Rooms_outlier'] = 0
        X.loc[(X['Rooms'] == 0) | (X['Rooms'] >= 5), 'Rooms_outlier'] = 1

        X.loc[X['Rooms'] == 0, 'Rooms'] = 1
        X.loc[X['Rooms'] > 5, 'Rooms'] = self.medians['Rooms']
        
        #Square
        X = X.merge(self.med_square_by_rooms_district, on=['Rooms', 'DistrictId'], how='left')
        X = X.merge(self.med_square_by_rooms, on='Rooms', how='left')
        
        condition = X['MedSquareByRoomsDistrictId'].isna()
        X.loc[condition, 'MedSquareByRoomsDistrictId'] = X.loc[condition, 'MedSquareByRooms']

        X['Square_outlier'] = 0
        condition = X['Square'] < self.square_quantile_025
        X.loc[condition, 'Square_outlier'] = 1
        X.loc[condition, 'Square'] = X.loc[condition, 'MedSquareByRoomsDistrictId']

        condition = X['Square'] > self.square_quantile_975
        X.loc[condition, 'Square_outlier'] = 1
        X.loc[condition, 'Square'] = X.loc[condition, 'MedSquareByRoomsDistrictId']


        #KitchenSquare
        X['KitchenSquare_outlier'] = 0

        condition = X['KitchenSquare'] < 1
        X.loc[condition, 'KitchenSquare'] = 1
        X.loc[condition, 'KitchenSquare_outlier'] = 1

        condition = X['KitchenSquare'] > self.kitchen_square_quantile
        X.loc[condition, 'KitchenSquare'] = self.kitchen_square_quantile
        X.loc[condition, 'KitchenSquare_outlier'] = 1



        #LifeSquare
        X['LifeSquare_NaN'] = 0
        X['LifeSquare_outlier'] = 0 

        condition = X['LifeSquare'].isnull()
        X.loc[condition, 'LifeSquare_NaN'] = 1
        X.loc[condition, 'LifeSquare'] = X.loc[condition, 'Square'] -\
                                                X.loc[condition, 'KitchenSquare'] - 3

        condition = X['LifeSquare'] < self.lifesquare_quantile_025
        X.loc[condition, 'LifeSquare_outlier'] = 1
        X.loc[condition, 'LifeSquare'] = self.lifesquare_quantile_975
        X['LifeSquare'].isna().sum(), (X['LifeSquare'] < 0).sum()

        #HouseYear
        X.loc[X['HouseYear'] > 2020, 'HouseYear'] = 2020


        #HouseFloor
        med_housefloor_by_district = X.groupby('DistrictId', as_index=False).agg({'Floor':'median'}).rename(columns={'Floor':'MedHouseFloorByDistrict'})
        X = X.merge(med_housefloor_by_district, on='DistrictId', how='left')

        condition = X['HouseFloor'] == 0
        X.loc[condition, 'HouseFloor'] = X.loc[condition, 'MedHouseFloorByDistrict']

        condition = X['HouseFloor'] < X['Floor']
        X.loc[condition, 'Floor'] = X.loc[condition, 'HouseFloor'].apply(lambda x: random.randint(1, int(x)))

        #Healthcare_1
        X.drop('Healthcare_1', axis=1, inplace=True)

        return X
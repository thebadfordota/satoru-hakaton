﻿

Функция ТригерСработал(Пользователь, Действие, Объект) Экспорт
	
	Запрос = Новый Запрос;
	Запрос.Текст = 
		"ВЫБРАТЬ
		|	EPA_Тригеры.Пользователь КАК Пользователь
		|ИЗ
		|	РегистрСведений.EPA_Тригеры КАК EPA_Тригеры
		|ГДЕ
		|	EPA_Тригеры.Пользователь = &Пользователь
		|	И EPA_Тригеры.ОбъектСистемы = &ОбъектСистемы
		|	И EPA_Тригеры.Действия = &Действия";
	                                                       
	Запрос.УстановитьПараметр("Действия", Действие);       
	Запрос.УстановитьПараметр("ОбъектСистемы", Справочники.ИдентификаторыОбъектовМетаданных.НайтиПоРеквизиту("ПолноеИмя", Объект.Метаданные().ПолноеИмя()));
	Запрос.УстановитьПараметр("Пользователь", Пользователь);
	Возврат НЕ Запрос.Выполнить().Пустой();
	
КонецФункции
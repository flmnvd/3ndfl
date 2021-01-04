# Комплексная программа расчёта налога по доходам от операций с финансовыми инструментами и подготовки декларации 3-НДФЛ для налоговой службы (ФНС)

**Программа на самой ранней стадии разработки и эксплуатации пока не готова. _Базовый функционал планируется закончить в первом квартале 2021 года для подачи отчётность 3-НДФЛ за 2020 год_**

Планируется поддержка всех типов активов и операций.
Реализован импорт отчётов Interactive Brokers. Планируется добавить так же возможность имопрта отчётов Freedom Finance.

Используется Python + Qt.

[Инструкция по импорту отчёта Interactive Brokers](./doc/import-ib-report.md)

Для сообщений об ошибках или предложений: ru3ndfl (а) gmail [dot] com

Будет неплохо если прикрепите свои отчёты. Это поможет в отладке.

Перед отправкой откройте CSV-файлы обычным текстовым редактором (например, Notepad) и удалите персональную информацию в начале файла ("Информация о счете").

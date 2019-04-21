#ifndef TARJETA_UI_H
#define TARJETA_UI_H

#include <QWidget>

namespace Ui {
class tarjeta_ui;
}

class tarjeta_ui : public QWidget
{
    Q_OBJECT

public:
    explicit tarjeta_ui(QWidget *parent = 0);
    ~tarjeta_ui();

private:
    Ui::tarjeta_ui *ui;
};

#endif // TARJETA_UI_H

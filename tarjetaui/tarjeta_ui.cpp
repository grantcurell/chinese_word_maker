#include "tarjeta_ui.h"
#include "ui_tarjeta_ui.h"

tarjeta_ui::tarjeta_ui(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::tarjeta_ui)
{
    ui->setupUi(this);
}

tarjeta_ui::~tarjeta_ui()
{
    delete ui;
}

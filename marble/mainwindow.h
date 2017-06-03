#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>

namespace Ui {
class MainWindow;
}

namespace Marble {
   class MarbleWidget;
   class GeoDataDocument;
}

class QNetworkAccessManager;
class QNetworkReply;

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = 0);
    ~MainWindow();

public slots:
    void updateLines(QNetworkReply* reply);
    void fetchUpdate();

private:
    bool eventFilter(QObject *object, QEvent *event);

    Ui::MainWindow *ui;
    Marble::MarbleWidget* mMapWidget;
    Marble::GeoDataDocument* mDocument;
    QNetworkAccessManager* mNAM;

    static const char* sURL;
};

#endif // MAINWINDOW_H

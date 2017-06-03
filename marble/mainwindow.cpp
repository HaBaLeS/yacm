#include "mainwindow.h"
#include "ui_mainwindow.h"

#include <QKeyEvent>
#include <QTimer>
#include <QDebug>
#include <QtNetwork/QNetworkAccessManager>
#include <QtNetwork/QNetworkReply>
#include <QtNetwork/QNetworkRequest>
#include <QJsonDocument>
#include <QJsonArray>

#include <marble/MarbleWidget.h>
#include <marble/MarbleModel.h>
#include <marble/AbstractFloatItem.h>
#include <marble/GeoDataLineString.h>
#include <marble/GeoDataDocument.h>
#include <marble/GeoDataTreeModel.h>
#include <marble/GeoDataPlacemark.h>
#include <marble/GeoDataLineStyle.h>
#include <marble/GeoDataStyle.h>

const char* MainWindow::sURL = "http://localhost:8080/data";

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent), ui(new Ui::MainWindow), mMapWidget(NULL), mDocument(NULL), mNAM(NULL) {
    ui->setupUi(this);

    mMapWidget = new Marble::MarbleWidget(this->centralWidget());
    mMapWidget->setProjection(Marble::Mercator);
    //mMapWidget->setProjection(Marble::Projection::Spherical);
    //mMapWidget->setMapThemeId("earth/openstreetmap/openstreetmap.dgml");
    mMapWidget->setMapThemeId("earth/bluemarble/bluemarble.dgml");
    //mMapWidget->setMapThemeId("earth/vectorosm/vectorosm.dgml");


    mMapWidget->setShowOverviewMap(false);
    mMapWidget->setShowCompass(false);
    mMapWidget->setShowCrosshairs(false);
    mMapWidget->setShowGrid(false);
    mMapWidget->setShowScaleBar(false);

    mMapWidget->setMapQualityForViewContext(Marble::MapQuality::OutlineQuality, Marble::ViewContext::Animation);
    mMapWidget->setAnimationsEnabled(true);

    foreach (Marble::AbstractFloatItem * floatItem, mMapWidget->floatItems()) {
        if (floatItem && floatItem->nameId() == "navigation") {
            floatItem->setVisible(false);
        }
     }

    mDocument = new Marble::GeoDataDocument;
    mMapWidget->model()->treeModel()->addDocument(mDocument);

    this->centralWidget()->layout()->addWidget(mMapWidget);
    this->centralWidget()->installEventFilter(this);

    mNAM = new QNetworkAccessManager(this);
    QObject::connect(mNAM, SIGNAL(finished(QNetworkReply*)), this, SLOT(updateLines(QNetworkReply*)));

    QTimer::singleShot(1000, this, SLOT(fetchUpdate()));
}

void MainWindow::updateLines(QNetworkReply* reply) {
    if(reply->error() != QNetworkReply::NoError) {
        qWarning() << "Error in network reply: "  << reply->error();
        QTimer::singleShot(1000, this, SLOT(fetchUpdate()));
        return;
    }

    for (const auto& feature : mDocument->featureList()) {
        mMapWidget->model()->treeModel()->removeFeature(feature);
    }

    Marble::GeoDataLineStyle lineStyle(QColor( 255, 255, 0, 80 ));
    lineStyle.setWidth(3);

    QSharedPointer<Marble::GeoDataStyle> style = QSharedPointer<Marble::GeoDataStyle>::create();
    style->setLineStyle(lineStyle);

    QString strReply = (QString)reply->readAll();

    QJsonDocument jsonResponse = QJsonDocument::fromJson(strReply.toUtf8());
    QJsonArray array = jsonResponse.array();
    for (const auto& coordSet : array) {
        QJsonObject coords = coordSet.toObject();

        Marble::GeoDataLineString* string = new Marble::GeoDataLineString();
        string->setTessellate(true);
        string->setAltitudeMode(Marble::AltitudeMode::ClampToGround);

        string->append(Marble::GeoDataCoordinates(coords["src_long"].toDouble(), coords["src_lat"].toDouble(), 0.0, Marble::GeoDataCoordinates::Degree));
        string->append(Marble::GeoDataCoordinates(coords["dst_long"].toDouble(), coords["dst_lat"].toDouble(), 0.0, Marble::GeoDataCoordinates::Degree));

        Marble::GeoDataPlacemark* place = new Marble::GeoDataPlacemark();
        place->setStyle(style);
        place->setGeometry(string);

        mMapWidget->model()->treeModel()->addFeature(mDocument, place);
    }

    QTimer::singleShot(1000, this, SLOT(fetchUpdate()));
}

void MainWindow::fetchUpdate() {
    mNAM->get(QNetworkRequest(QUrl(sURL)));
}

bool MainWindow::eventFilter(QObject *object, QEvent *event) {
    if (object == this->centralWidget() && event->type() == QEvent::KeyPress) {
        QKeyEvent *ke = reinterpret_cast<QKeyEvent *>(event);
        if (ke->key() == Qt::Key_Escape) {
            this->close();
           return true;
        }
    } else {
        return false;
    }
}

MainWindow::~MainWindow() {
    delete ui;
}
